import uuid
import time
from typing import Optional, Any, Dict
from jupyter_client.connect import find_connection_file
from jupyter_client.blocking.client import BlockingKernelClient
from jupyter_core.paths import jupyter_runtime_dir
from queue import Empty, Queue
import json
import threading
import urllib
import websocket
import ssl
import urllib.parse
from urllib.parse import urlparse, urlunparse

from .schema import Cell, CodeCell, CellMetadata, Output, ExecuteResult, DisplayData, Stream, Error, Notebook, ContentResponseModel
import logging
import os
import requests
from contextlib import AbstractContextManager

logger = logging.getLogger(__name__)

JUPYTER_RUNTIME_PATH = jupyter_runtime_dir()
DEFAULT_EXECUTION_WAIT_TIMEOUT = 60

def find_connection_info_file_path(kernel_id: str) -> Optional[str]:
    """
    find connection info from project path and jupyter runtime path
    """
    try:
        connection_info_path = find_connection_file(
            filename=f"kernel-{kernel_id}.json"
        )
    except OSError:
        print(f'Can not find connection info file \
            kernel-{kernel_id}.json in {JUPYTER_RUNTIME_PATH}')
        return None
    return connection_info_path


def execute_and_capture_output(
    client: "RemoteKernelClientManager",
    code: str,
    read_channel_timeout: int,
    execution_timeout: int
) -> tuple[CodeCell, bool]:
    """Execute code via kernel client and capture the output"""

    msg_id = client.execute(code)
    execute_count = None
    outputs: list[Output] = []
    is_timeout = False

    start_time = time.time()

    while True:
        if time.time() - start_time > execution_timeout:
            is_timeout = True
            break

        try:
            msg = client.get_iopub_msg(timeout=read_channel_timeout)
            if msg["parent_header"]["msg_id"] != msg_id:
                continue

            msg_type = msg["header"]["msg_type"]
            content = msg["content"]

            if msg_type == "status":
                if content["execution_state"] == "idle":
                    # Execution completed
                    break

            elif msg_type == "execute_input":
                execute_count = content["execution_count"]

            elif msg_type == "execute_result":
                # Results from the execution
                outputs.append(
                    ExecuteResult(
                        output_type="execute_result",
                        execution_count=content.get("execution_count"),
                        data=content["data"],
                        metadata=content.get("metadata", {})
                    )
                )

            elif msg_type == "display_data":
                # Display data (like plots, images, etc.)
                outputs.append(
                    DisplayData(
                        output_type="display_data",
                        data=content["data"],
                        metadata=content.get("metadata", {})
                    )
                )

            elif msg_type == "stream":
                # Standard output/error streams
                outputs.append(
                    Stream(
                        output_type="stream",
                        name=content["name"],  # 'stdout' or 'stderr'
                        text=content["text"]
                    )
                )

            elif msg_type == "error":
                # Errors during execution
                outputs.append(
                    Error(
                        output_type="error",
                        ename=content["ename"],
                        evalue=content["evalue"],
                        traceback=content["traceback"]
                    )
                )

        except KeyError:
            # Skip malformed messages
            continue

        except Empty:
            # If we timeout waiting for a message, check if kernel is still alive
            logger.debug("Timeout waiting for a message, check if kernel is still alive")
            if not client.is_alive():
                logger.warning("Kernel is not alive")
                break

    # Get the execution reply message to ensure we have the final execution count
    try:
        reply = client.get_shell_msg(timeout=read_channel_timeout)
        if reply["parent_header"]["msg_id"] == msg_id:
            if execute_count is None:
                execute_count = reply["content"].get("execution_count")
    except Exception:
        # If we can't get the shell message, continue with what we have
        pass

    return CodeCell(
        id = uuid.uuid4().hex,
        cell_type = "code",
        metadata = CellMetadata(),
        source = code,
        outputs = outputs,
        execution_count=execute_count
    ), is_timeout


class KernelClientManager(AbstractContextManager):
    """context manager for kernel client"""

    def __init__(self, connection_info_path: str):
        """initialize kernel client manager

        Args:
            connection_info_path: connection info file path
        """
        self.connection_info_path = connection_info_path
        self.client = None

    def __enter__(self) -> BlockingKernelClient:
        """enter context, create and start client

        Returns:
            BlockingKernelClient: started kernel client
        """
        self.client = BlockingKernelClient()
        # load connection file (from jupyter_client.connect.ConnectionFileMixin)
        self.client.load_connection_file(self.connection_info_path)
        self.client.start_channels()
        return self.client

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """exit context, close client resources

        Args:
            exc_type: exception type
            exc_val: exception value
            exc_tb: exception traceback
        """
        if self.client is not None:
            self.client.stop_channels()
            self.client = None


class RemoteKernelClientManager(AbstractContextManager):
    """Context manager for remote kernel client if jupyter server is deployed at remote

    This class provides a similar interface to KernelClientManager but works with
    remote Jupyter kernels via WebSocket connections.
    """

    def __init__(self, kernel_id: str):
        """Initialize remote kernel client manager

        Args:
            kernel_id: ID of the remote kernel to connect to
        """
        self.kernel_id = kernel_id
        self.ws = None
        self.ws_connected = False
        self.msg_queue: Dict[str, Queue] = {
            'iopub': Queue(),
            'shell': Queue(),
            'stdin': Queue(),
            'control': Queue()
        }
        self.channels = ['iopub', 'shell', 'stdin', 'control']
        self._lock = threading.RLock()
        self._receiver_thread = None
        self._stop_event = threading.Event()  # add stop event to control receiver thread

        # Get environment variables for remote connection
        self.server_url = os.getenv('JUPYTER_SERVER_URL')
        self.server_token = os.getenv('JUPYTER_SERVER_TOKEN')
        # TODO: we need to take attention to the base url of jupyter server

        if not self.server_url or not self.server_token:
            raise ValueError("Both JUPYTER_SERVER_URL and JUPYTER_SERVER_TOKEN environment variables must be set")

        # Convert HTTP(S) URL to WebSocket URL using URL parsing
        parsed_url = urlparse(self.server_url)

        # Map http -> ws, https -> wss
        ws_scheme = 'wss' if parsed_url.scheme == 'https' else 'ws'

        # Reconstruct the base URL with WebSocket scheme
        self.ws_url_base = urlunparse((
            ws_scheme,
            parsed_url.netloc,
            parsed_url.path.rstrip('/'),  # Remove trailing slash using rstrip
            '',
            '',
            ''
        ))

        # Construct WebSocket URL for kernel
        self.ws_url = f"{self.ws_url_base}/api/kernels/{self.kernel_id}/channels?token={urllib.parse.quote(self.server_token)}"

        logger.debug(f"Remote kernel WebSocket URL: {self.ws_url}")

    def __enter__(self):
        """Enter context, establish WebSocket connection to remote kernel

        Returns:
            self: This object provides an interface similar to BlockingKernelClient
        """
        try:
            # Create WebSocket connection
            self.ws = websocket.create_connection(
                self.ws_url,
                sslopt={"cert_reqs": ssl.CERT_NONE} if self.ws_url.startswith("wss://") else {},
                timeout=10
            )
            self.ws_connected = True

            # reset stop event
            self._stop_event.clear()

            # Start message receiving thread
            self._receiver_thread = threading.Thread(target=self._receive_messages)
            self._receiver_thread.daemon = True
            self._receiver_thread.start()

            logger.info(f"Connected to remote kernel {self.kernel_id}")
            return self
        except Exception as e:
            logger.error(f"Failed to connect to remote kernel: {e}")
            self.ws_connected = False
            if self.ws:
                self.ws.close()
                self.ws = None
            raise

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context, disconnect WebSocket connection

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        # set stop event to notify receiver thread to exit
        self._stop_event.set()

        # close WebSocket connection
        if self.ws and self.ws_connected:
            try:
                self.ws.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket connection: {e}")
            finally:
                self.ws = None
                self.ws_connected = False

        # Since the receiver thread is a daemon thread (daemon=True),
        # we don't need to explicitly join it as it won't prevent the program from exiting
        # and the stop event will signal it to terminate naturally

        # clear message queue
        for channel in self.channels:
            try:
                while not self.msg_queue[channel].empty():
                    self.msg_queue[channel].get_nowait()
            except Exception:
                pass

        logger.info(f"Disconnected from remote kernel {self.kernel_id}")

    def _receive_messages(self):
        """Background thread to receive messages from WebSocket and route them to appropriate queues"""
        while not self._stop_event.is_set() and self.ws_connected and self.ws:
            try:
                # add timeout to check stop event
                self.ws.settimeout(0.5)
                msg_str = self.ws.recv()
                msg = json.loads(msg_str)

                # Route message to appropriate queue based on channel
                channel = msg.get('channel', '')
                if channel in self.channels:
                    self.msg_queue[channel].put(msg)
                else:
                    logger.warning(f"Received message with unknown channel: {channel}")
            except websocket.WebSocketTimeoutException:
                # timeout to check stop event
                continue
            except websocket.WebSocketConnectionClosedException:
                logger.info("WebSocket connection closed")
                self.ws_connected = False
                break
            except Exception as e:
                if not self._stop_event.is_set():  # only log error when not in stop state
                    logger.error(f"Error receiving message: {e}")
                continue

    def execute(self, code: str) -> str:
        """Execute code on the remote kernel

        Args:
            code: Code to execute

        Returns:
            msg_id: Message ID for tracking execution
        """
        if not self.ws_connected or not self.ws:
            raise RuntimeError("Not connected to remote kernel")

        msg_id = uuid.uuid4().hex

        # Create execute_request message
        msg = {
            'header': {
                'msg_id': msg_id,
                'username': 'remote_client',
                'session': uuid.uuid4().hex,
                'date': time.strftime('%Y-%m-%dT%H:%M:%S.%f'),
                'msg_type': 'execute_request',
                'version': '5.0'
            },
            'parent_header': {},
            'metadata': {},
            'content': {
                'code': code,
                'silent': False,
                'store_history': True,
                'user_expressions': {},
                'allow_stdin': False,
                'stop_on_error': True
            },
            'channel': 'shell',
            'buffers': []
        }

        # Send message
        with self._lock:
            self.ws.send(json.dumps(msg))

        return msg_id

    def get_iopub_msg(self, timeout: Optional[float] = None) -> Dict:
        """Get a message from the iopub channel

        Args:
            timeout: How long to wait for a message (in seconds)

        Returns:
            Message from iopub channel

        Raises:
            Empty: If no message is available within the timeout
        """
        try:
            return self.msg_queue['iopub'].get(timeout=timeout)
        except Exception:
            raise Empty("No messages available on iopub channel")

    def get_shell_msg(self, timeout: Optional[float] = None) -> Dict:
        """Get a message from the shell channel

        Args:
            timeout: How long to wait for a message (in seconds)

        Returns:
            Message from shell channel

        Raises:
            Empty: If no message is available within the timeout
        """
        try:
            return self.msg_queue['shell'].get(timeout=timeout)
        except Exception:
            raise Empty("No messages available on shell channel")

    def is_alive(self) -> bool:
        """Check if the kernel is alive

        Returns:
            True if the kernel is alive, False otherwise
        """
        return self.ws_connected and self.ws is not None


def execute_code_with_client(kernel_id: str, code: str) -> tuple[CodeCell, bool]:

    with RemoteKernelClientManager(kernel_id) as client:
        # execute code
        code_cell, run_timeout = execute_and_capture_output(
            client,
            code,
            read_channel_timeout=1,
            execution_timeout=int(os.getenv("WAIT_EXECUTION_TIMEOUT", DEFAULT_EXECUTION_WAIT_TIMEOUT))
        )

    return code_cell, run_timeout

def get_kernel_by_notebook_path(notebook_path: str) -> Optional[str]:
    """Get kernel id by notebook path (here notebook path should be a relative path according to the root dir of the jupyter server)"""
    # Get environment variables
    server_url = os.getenv('JUPYTER_SERVER_URL') # here SERVER_URL should be {schema}://{host}:{port}/{base_url}
    server_token = os.getenv('JUPYTER_SERVER_TOKEN')

    if not server_url or not server_token:
        raise ValueError("Both JUPYTER_SERVER_URL and JUPYTER_SERVER_TOKEN environment variables must be set")

    # Construct the API endpoint
    api_url = f"{server_url}/api/sessions?token={server_token}"
    logger.info(f"Fetching sessions from {api_url}")


    response = requests.get(api_url)
    response.raise_for_status()  # Raise an exception for bad status codes
    sessions = response.json()

    # Find the session that matches the notebook path
    for session in sessions:
        if session.get('path') == notebook_path:
            return session.get('kernel', {}).get('id')

    return None

def add_new_cell_to_notebook(notebook_path: str, cell: Cell) -> None:
    """Add new cell to notebook"""
    # Get environment variables
    server_url = os.getenv('JUPYTER_SERVER_URL') # here SERVER_URL should be {schema}://{host}:{port}/{base_url}
    server_token = os.getenv('JUPYTER_SERVER_TOKEN')

    if not server_url or not server_token:
        raise ValueError("Both JUPYTER_SERVER_URL and JUPYTER_SERVER_TOKEN environment variables must be set")

    # Construct the API endpoint
    api_url = f"{server_url}/api/contents/{notebook_path}?token={server_token}"

    notebook_contents = requests.get(api_url)
    notebook_contents.raise_for_status()  # Raise an exception for bad status codes

    # Add the new cell to the notebook
    notebook_model = Notebook.model_validate(notebook_contents.json()["content"])

    notebook_model.cells.append(cell)

    # Update the notebook
    response = requests.put(api_url, json={
        "content": notebook_model.model_dump(),
        "type": "notebook",
        "format": "json"
    })
    response.raise_for_status()
    return


def locate_idx_for_cell_with_given_id(notebook_model: Notebook, cell_id: str) -> Optional[int]:
    cell_idx_to_replace = next(
        (idx for idx, cell in enumerate(notebook_model.cells) if cell.id == cell_id),
        None
    )

    return cell_idx_to_replace


def replace_cell_in_notebook(notebook_path: str, notebook: Notebook, cell: Cell, cell_idx: int) -> None:
    """ we should replace the cell with the given idx with the cell
    """
    # Get environment variables
    server_url = os.getenv('JUPYTER_SERVER_URL') # here SERVER_URL should be {schema}://{host}:{port}/{base_url}
    server_token = os.getenv('JUPYTER_SERVER_TOKEN')

    if not server_url or not server_token:
        raise ValueError("Both JUPYTER_SERVER_URL and JUPYTER_SERVER_TOKEN environment variables must be set")

    # Construct the API endpoint
    api_url = f"{server_url}/api/contents/{notebook_path}?token={server_token}"
    # Replace the cell
    notebook.cells[cell_idx] = cell

    # Update the notebook
    response = requests.put(api_url, json={
        "content": notebook.model_dump(),
        "type": "notebook",
        "format": "json"
    })
    response.raise_for_status()
    return


def get_content(file_path: str) -> ContentResponseModel:
    # Get environment variables
    server_url = os.getenv('JUPYTER_SERVER_URL') # here SERVER_URL should be {schema}://{host}:{port}/{base_url}
    server_token = os.getenv('JUPYTER_SERVER_TOKEN')

    if not server_url or not server_token:
        raise ValueError("Both JUPYTER_SERVER_URL and JUPYTER_SERVER_TOKEN environment variables must be set")

    # Construct the API endpoint
    api_url = f"{server_url}/api/contents/{file_path}?token={server_token}"

    # Send GET request to retrieve file content
    response = requests.get(api_url)
    response.raise_for_status()  # Raise an exception for bad status codes

    # Parse the response and validate the model
    content_model = ContentResponseModel.model_validate(response.json())

    return content_model
