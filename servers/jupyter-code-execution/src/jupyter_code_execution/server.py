import os
import logging
from typing import Annotated
from mcp.server import FastMCP
from pydantic import Field
from mcp.types import TextContent
from jupyter_code_execution.schema import LanguageInfo, Notebook, NotebookMetadata, KernelSpec
from jupyter_code_execution.utils import add_new_cell_to_notebook, execute_and_capture_output, get_kernel_by_notebook_path, RemoteKernelClientManager

DEFAULT_EXECUTION_WAIT_TIMEOUT = 60

mcp = FastMCP(name="jupyter", description="Jupyter MCP Server for Code Execution")
logger = logging.getLogger(__name__)

@mcp.tool(
    name="new_notebook",
    description="Create a new notebook with empty cells"
)
def new_notebook() -> Notebook:
    """ Create a new notebook with empty kernelspec and language_info, if we have a kernel running, we could
    get the metadata through kernel client.
    """
    return Notebook(
        metadata=NotebookMetadata(
            kernelspec=KernelSpec(
                name="",
                display_name="",
            ),
            language_info=LanguageInfo(
                codemirror_mode={"name": "ipython", "version": 3},
                file_extension=".py",
                mimetype="text/x-python",
                name="python",
                pygments_lexer="ipython3",
            )
        ),
        nbformat_minor=5,
        nbformat=4,
        cells=[]
    )

@mcp.tool(
    name="execute_code",
    description="Execute code in a notebook with specific notebook path"
)
def execute_code(
    notebook_path: Annotated[str, Field(..., description="A relative path to the notebook file")],
    code: Annotated[str, Field(..., description="Code to execute")],
) -> list[TextContent]:
    """ Execute code in a notebook with specific notebook path """
    kernel_id = get_kernel_by_notebook_path(notebook_path)
    if kernel_id is None:
        return [
            TextContent(
                type="text",
                text=f"Can not find kernel id with notebook path: {notebook_path}, please make sure the session is running on this notebook"
            )
        ]

    # connection_info_path = find_connection_info_file_path(kernel_id)
    # if connection_info_path is None:
    #     return [
    #         TextContent(
    #             type="text",
    #             text=f"Can not find connection info file with kernel_id: {kernel_id}"
    #         )
    #     ]


    # use context manager to manage client resources
    with RemoteKernelClientManager(kernel_id) as client:
        # execute code
        code_cell, run_timeout = execute_and_capture_output(
            client,
            code,
            read_channel_timeout=1,
            execution_timeout=int(os.getenv("WAIT_EXECUTION_TIMEOUT", DEFAULT_EXECUTION_WAIT_TIMEOUT))
        )

    if run_timeout:
        return [
            TextContent(
                type="text",
                text="Waiting execution result timed out. The kernel may still be running the code."
            )
        ]

    return [
        TextContent(
            type="text",
            text=code_cell.model_dump_json()
        )
    ]


@mcp.tool(
    name="add_cell_and_execute_code",
    description="Add a cell to the notebook and execute it"
)
def add_cell_and_execute_code(
    notebook_path: Annotated[str, Field(..., description="A relative path to the notebook file")],
    code: Annotated[str, Field(..., description="Code to execute")],
) -> list[TextContent]:
    """ Add a cell to the notebook and execute it """
    kernel_id = get_kernel_by_notebook_path(notebook_path)
    if kernel_id is None:
        return [
            TextContent(
                type="text",
                text=f"Can not find kernel id with notebook path: {notebook_path}, please make sure the session is running on this notebook"
            )
        ]

    # connection_info_path = find_connection_info_file_path(kernel_id)
    # if connection_info_path is None:
    #     return [
    #         TextContent(
    #             type="text",
    #             text=f"Can not find connection info file with kernel_id: {kernel_id}"
    #         )
    #     ]

    # use context manager to manage client resources
    with RemoteKernelClientManager(kernel_id) as client:
        # execute code
        code_cell, run_timeout = execute_and_capture_output(
            client,
            code,
            read_channel_timeout=1,
            execution_timeout=int(os.getenv("WAIT_EXECUTION_TIMEOUT", DEFAULT_EXECUTION_WAIT_TIMEOUT))
        )

    if run_timeout:
        return [
            TextContent(
                type="text",
                text="Waiting execution result timed out. The kernel may still be running the code."
            )
        ]

    # add cell to notebook with put method
    try:
        add_new_cell_to_notebook(notebook_path, code_cell)
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Failed to add cell to notebook: {e}"
            )
        ]

    return [
        TextContent(
            type="text",
            text=code_cell.model_dump_json()
        )
    ]

# read notebook

# list sessions

# list kernels

# list notebooks

# find running local jupyter server -> find executable jupyter command
