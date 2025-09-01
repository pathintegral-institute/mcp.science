import io
import logging
import os
from pathlib import Path
from typing import Optional, Tuple

import paramiko
from paramiko.config import SSHConfig

logger = logging.getLogger(__name__)


class SSHClient:
    """SSH client for executing commands on remote systems"""

    def __init__(
        self,
        host: str,
        port: int = 22,
        username: Optional[str] = None,
        private_key_file: Optional[str] = None,
        password: Optional[str] = None,
        ssh_config_file: Optional[str] = None,
    ):
        """Initialize SSH client

        Args:
            host: SSH host to connect to
            port: SSH port (defaults to 22)
            username: SSH username (optional if specified in SSH config)
            private_key_file: SSH private key file path
            password: SSH password
            ssh_config_file: Path to SSH config file (defaults to ~/.ssh/config)

        Note:
            If username is not provided, it will be read from SSH config
            If neither private_key_file nor password is provided, the client will attempt
            to use SSH config identity files or system SSH configuration (e.g., keys in ~/.ssh/)
            SSH config file is loaded as fallback for missing connection parameters
        """
        self.host = host
        self.port = port
        self.username = username
        self.private_key_file = private_key_file
        self.password = password
        self.ssh_config_file = ssh_config_file
        self.client = None
        self._ssh_config = None

    def _get_default_ssh_config_path(self) -> Optional[str]:
        """Get the default SSH config file path for the current platform."""
        config_path = Path.home() / '.ssh' / 'config'
        
        return str(config_path) if config_path.exists() else None

    def _load_ssh_config(self) -> Optional[SSHConfig]:
        """Load SSH config from file."""
        if self._ssh_config is not None:
            return self._ssh_config

        config_path = self.ssh_config_file or self._get_default_ssh_config_path()
        if not config_path:
            return None

        try:
            self._ssh_config = SSHConfig.from_path(config_path)
            logger.debug("Loaded SSH config from %s", config_path)
            return self._ssh_config
        except (IOError, OSError) as e:
            logger.warning(
                "Could not load SSH config from %s: %s",
                config_path, str(e)
            )
            return None

    def _get_config_for_host(self, hostname: str) -> dict:
        """Get SSH config settings for a specific hostname."""
        ssh_config = self._load_ssh_config()
        if ssh_config:
            return ssh_config.lookup(hostname)
        return {}

    def _load_private_key_file(self, key_file_path: str) -> Optional[paramiko.PKey]:
        """Load private key from file, trying multiple key types."""
        if not os.path.exists(key_file_path):
            logger.debug("Key file not found: %s", key_file_path)
            return None

        key_types = [
            paramiko.RSAKey,
            paramiko.Ed25519Key,
            paramiko.ECDSAKey,
        ]
        
        for key_type in key_types:
            try:
                private_key = key_type.from_private_key_file(key_file_path)
                logger.debug("Loaded %s key from %s", key_type.__name__, key_file_path)
                return private_key
            except (paramiko.SSHException, ValueError, OSError):
                continue
        logger.warning("Unable to load private key from %s", key_file_path)
        return None

    def _set_system_auth(self, connect_kwargs: dict) -> None:
        """Set up system authentication fallback."""
        logger.info("Using system SSH configuration for authentication")
        connect_kwargs["look_for_keys"] = True
        connect_kwargs["allow_agent"] = True

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

            # Get SSH config settings for this host
            config_settings = self._get_config_for_host(self.host)
            
            # Use SSH config values as fallbacks
            hostname = config_settings.get('hostname', self.host)
            port = config_settings.get('port', self.port)
            username = self.username or config_settings.get('user')
            
            # Convert port to int if it's a string from config
            if isinstance(port, str):
                port = int(port)
                
            # Username is required for SSH connection
            if not username:
                raise paramiko.SSHException(
                    f"No username specified for host {self.host}. "
                    "Please provide username parameter or configure it in SSH config."
                )

            connect_kwargs = {
                "hostname": hostname,
                "port": port,
                "username": username,
            }

            # Handle authentication - check explicit params first, then SSH config
            if self.private_key_file:
                # Use explicitly provided private key file
                private_key = self._load_private_key_file(self.private_key_file)
                if private_key:
                    connect_kwargs["pkey"] = private_key
            elif self.password:
                # Use explicitly provided password
                connect_kwargs["password"] = self.password
            elif config_settings.get('identityfile'):
                # Try SSH config identity files
                identity_files = config_settings.get('identityfile')
                if isinstance(identity_files, str):
                    identity_files = [identity_files]
                
                private_key = None
                for identity_file in identity_files:
                    # Expand ~ to home directory
                    identity_file = os.path.expanduser(identity_file)
                    private_key = self._load_private_key_file(identity_file)
                    if private_key:
                        connect_kwargs["pkey"] = private_key
                        break
                
                if not private_key:
                    # Fall back to system authentication
                    self._set_system_auth(connect_kwargs)
            else:
                # If nothing is explicitly configured, use system SSH config
                self._set_system_auth(connect_kwargs)

            self.client.connect(**connect_kwargs)
            logger.info(
                "Connected to SSH server %s:%s",
                connect_kwargs["hostname"],
                connect_kwargs["port"]
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
                "Disconnected from SSH server"
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
