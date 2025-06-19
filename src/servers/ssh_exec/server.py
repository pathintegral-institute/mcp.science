import logging
import os
from typing import Literal, Optional, Tuple
from functools import lru_cache
from typing import Annotated

import paramiko
from fastapi import HTTPException
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from .ssh_client import SSHClient
from .utils import validate_command
from pydantic import BaseModel, Field
import json

logger = logging.getLogger(__name__)

# Global variables for configuration
SSH_HOST = None
SSH_PORT = 22
SSH_USERNAME = None
SSH_PRIVATE_KEY = None
SSH_PASSWORD = None
ALLOWED_COMMANDS = []
ALLOWED_PATHS = []
COMMANDS_BLACKLIST = []
ARGUMENTS_BLACKLIST = []


def load_env():
    """Load environment variables"""
    global SSH_HOST, SSH_PORT, SSH_USERNAME
    global SSH_PRIVATE_KEY, SSH_PASSWORD
    global ALLOWED_COMMANDS, ALLOWED_PATHS
    global COMMANDS_BLACKLIST, ARGUMENTS_BLACKLIST

    # Get SSH configuration from environment variables
    SSH_HOST = os.environ.get("SSH_HOST")
    SSH_PORT = int(os.environ.get("SSH_PORT", "22"))
    SSH_USERNAME = os.environ.get("SSH_USERNAME")
    SSH_PRIVATE_KEY = os.environ.get("SSH_PRIVATE_KEY")
    SSH_PASSWORD = os.environ.get("SSH_PASSWORD")

    # Get security configuration from environment variables
    ALLOWED_COMMANDS = [
        cmd.strip() for cmd in os.environ.get("SSH_ALLOWED_COMMANDS", "").split(",")
        if cmd.strip()
    ]
    ALLOWED_PATHS = [path.strip() for path in os.environ.get(
        "SSH_ALLOWED_PATHS", "").split(",") if path.strip()]
    COMMANDS_BLACKLIST = [cmd.strip() for cmd in os.environ.get(
        "SSH_COMMANDS_BLACKLIST", "rm,mv,dd,mkfs,fdisk,format").split(",") if cmd.strip()]
    ARGUMENTS_BLACKLIST = [arg.strip() for arg in os.environ.get(
        "SSH_ARGUMENTS_BLACKLIST", "-rf,-fr,--force").split(",") if arg.strip()]

    # Log configuration (without sensitive data)
    logger.info("SSH exec MCP server configuration:")
    logger.info("SSH host: %s", SSH_HOST)
    logger.info("SSH port: %s", SSH_PORT)
    logger.info("SSH username: %s", SSH_USERNAME)
    logger.info("Using private key: %s", bool(SSH_PRIVATE_KEY))
    logger.info("Using password: %s", bool(SSH_PASSWORD))
    logger.info(
        "Using system SSH config: %s", not SSH_PRIVATE_KEY and not SSH_PASSWORD)
    logger.info("Allowed commands: %s", ALLOWED_COMMANDS)
    logger.info("Allowed paths: %s", ALLOWED_PATHS)
    logger.info("Commands blacklist: %s", COMMANDS_BLACKLIST)
    logger.info("Arguments blacklist: %s", ARGUMENTS_BLACKLIST)


class ExecuteCommand(BaseModel):
    """Arguments for the ssh-exec tool"""
    command: str = Field(description="Command to execute on the remote system")
    arguments: Optional[str] = Field(
        default=None, description="Arguments to pass to the command")
    timeout: Optional[int] = Field(
        default=None, description="Timeout in seconds for command execution")


# Create an MCP server
mcp = FastMCP("mcp-ssh-exec")


# Validate SSH configuration
def validate_ssh_config() -> None:
    """Validate SSH configuration

    Raises:
        ValueError: If any required configuration is missing
    """
    if not SSH_HOST:
        raise ValueError("SSH_HOST environment variable is not set")
    if not SSH_USERNAME:
        raise ValueError("SSH_USERNAME environment variable is not set")
    # Private key and password are now optional
    # If neither is provided, system SSH configuration will be used


# Get or create SSH client
@lru_cache
def get_ssh_client() -> Optional[SSHClient]:
    """Get or create SSH client

    Returns:
        SSH client instance or None if configuration is invalid
    """

    # Create SSH client if it doesn't exist
    try:
        ssh_client = SSHClient(
            host=SSH_HOST,
            port=SSH_PORT,
            username=SSH_USERNAME,
            private_key=SSH_PRIVATE_KEY,
            password=SSH_PASSWORD
        )
        logger.info(
            "Created SSH client for %s@%s:%s",
            SSH_USERNAME, SSH_HOST, SSH_PORT)
        return ssh_client
    except paramiko.SSHException as e:
        logger.error("Failed to create SSH client: %s", str(e))
        return None


# Add the SSH exec tool
@mcp.tool()
async def ssh_exec(
    command: Annotated[str, Field(
        description="Command for SSH server to execute")],
    arguments: Annotated[Optional[str], Field(
        description="Arguments to pass to the command")] = None,
    timeout: Annotated[Optional[int], Field(
        description="Timeout in seconds for command execution")] = None
) -> Tuple[int, str, str]:
    """Execute a command on the remote system

    Args:
        command: Command to execute
        arguments: Arguments to pass to the command
        timeout: Optional timeout in seconds for command execution

    Returns:
        Tuple containing (exit_code, stdout, stderr)

    Raises:
        HTTPException: If the command validation fails or the SSH connection fails
    """
    # Validate SSH configuration
    try:
        validate_ssh_config()
    except ValueError as e:
        logger.error("SSH configuration error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f'SSH configuration error: {str(e)}'
        ) from e

    # Build the full command
    full_command = command
    if arguments:
        full_command = f"{command} {arguments}"

    # Validate command against security constraints
    validate_command(
        full_command,
        ALLOWED_COMMANDS,
        ALLOWED_PATHS,
        COMMANDS_BLACKLIST,
        ARGUMENTS_BLACKLIST
    )

    # Get SSH client
    client = get_ssh_client()

    if not client:
        error_msg = "Failed to create SSH client. Check server logs for details."
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

    try:
        # Execute command
        await client.connect()
        exit_code, stdout, stderr = await client.execute_command(
            command=full_command, timeout=timeout)

        logger.info("Executed command: %s, exit code: %s", command, exit_code)
        # return the TextContent for all outputs
        return TextContent(
            type="text",
            text=json.dumps({
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr
            })
        )
    except Exception as e:
        logger.error(
            "Failed to execute command: %s, error: %s", full_command, str(e))
        error_msg = f"Failed to execute command: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if client:
            await client.disconnect()


# Load configuration at module initialization time
# This is safe because we're using global variables that are initialized with defaults
try:
    load_env()
    logger.info("Configuration loaded successfully")

    # Test SSH configuration
    try:
        validate_ssh_config()
        logger.info("SSH configuration is valid")
    except ValueError as e:
        logger.warning("SSH configuration warning: %s", str(e))
        logger.warning(
            "SSH commands will fail until the configuration is fixed")
except Exception as e:
    logger.error("Failed to load configuration: %s", str(e))
    logger.error("The server will start, but SSH commands may fail")


def main(transport: Literal["stdio", "sse"] = "stdio") -> None:
    """Initialize and run the SSH execution MCP server with stdio transport.

    This function serves as the entry point when the module is imported and used
    by other modules. It starts the FastMCP server using stdio transport, which
    is suitable for integration with MCP clients.
    """
    # Initialize and run the server
    logger.info("starting ssh exec server...")
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
