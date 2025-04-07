import io
import logging
from typing import Optional, Tuple

import paramiko

logger = logging.getLogger(__name__)


class SSHClient:
    """SSH client for executing commands on remote systems"""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        private_key: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Initialize SSH client

        Args:
            host: SSH host to connect to
            port: SSH port
            username: SSH username
            private_key: SSH private key content (not path)
            password: SSH password

        Note:
            If neither private_key nor password is provided, the client will attempt
            to use the system's SSH configuration (e.g., keys in ~/.ssh/)
        """
        self.host = host
        self.port = port
        self.username = username
        self.private_key = private_key
        self.password = password
        self.client = None

    async def connect(self) -> None:
        """Connect to the SSH server"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Load system host keys if available
            try:
                self.client.load_system_host_keys()
            except (IOError, paramiko.SSHException) as e:
                logger.warning(
                    "Could not load system host keys: {error}",
                    error=str(e)
                )

            connect_kwargs = {
                "hostname": self.host,
                "port": self.port,
                "username": self.username,
            }

            if self.private_key:
                key_file = io.StringIO(self.private_key)
                private_key = paramiko.RSAKey.from_private_key(key_file)
                connect_kwargs["pkey"] = private_key
            elif self.password:
                connect_kwargs["password"] = self.password
            else:
                # If neither private_key nor password is provided, use system SSH config
                # This will use keys from ~/.ssh/ if available
                logger.info(
                    "Using system SSH configuration for authentication")
                connect_kwargs["look_for_keys"] = True
                connect_kwargs["allow_agent"] = True

            self.client.connect(**connect_kwargs)
            logger.info(
                "Connected to SSH server %s:%s",
                self.host,
                self.port
            )
        except paramiko.SSHException as e:
            logger.error(
                "Failed to connect to SSH server: %s",
                str(e)
            )
            raise

    async def disconnect(self) -> None:
        """Disconnect from the SSH server"""
        if self.client:
            self.client.close()
            self.client = None
            logger.info(
                "Disconnected from SSH server %s:%s",
                self.host,
                self.port
            )

    async def execute_command(
        self,
        command: str,
        timeout: Optional[int] = None
    ) -> Tuple[int, str, str]:
        """Execute a command on the remote system

        Args:
            command: Command to execute
            timeout: Optional timeout in seconds for executing the command,
                the number of seconds to wait for a pending read or write
                operation before raising a socket.timeout error. Set to None
                to disable the timeout.

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if not self.client:
            await self.connect()

        try:
            # Ignore stdin as it's not used
            _, stdout, stderr = self.client.exec_command(
                command=command, timeout=timeout
            )
            exit_code = stdout.channel.recv_exit_status()
            stdout_str = stdout.read().decode("utf-8")
            stderr_str = stderr.read().decode("utf-8")

            logger.info(
                "Executed command: %s, exit code: %s",
                command, exit_code
            )
            return exit_code, stdout_str, stderr_str
        except paramiko.SSHException as e:
            logger.error(
                "Failed to execute command: %s, error: %s",
                command,
                str(e)
            )
            raise
        except Exception as e:
            logger.error(
                "Unexpected error executing command: %s, error: %s",
                command,
                str(e)
            )
            raise
