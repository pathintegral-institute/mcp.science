from dotenv import load_dotenv
import argparse
import logging
import os


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
# Get the directory of the current file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)
logger.info(f"Loaded environment variables from {dotenv_path}")


def parse_arguments():
    """Parse command line arguments for the SSH execution MCP server.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="SSH execution MCP server")

    # SSH connection configuration
    ssh_group = parser.add_argument_group("SSH Connection Configuration")
    ssh_group.add_argument(
        "--ssh-host", "-sh",
        type=str,
        help="SSH host to connect to (overrides SSH_HOST environment variable)"
    )
    ssh_group.add_argument(
        "--ssh-port", "-sp",
        type=int,
        help="SSH port to connect to (overrides SSH_PORT environment variable)"
    )
    ssh_group.add_argument(
        "--ssh-username", "-su",
        type=str,
        help="SSH username (overrides SSH_USERNAME environment variable)"
    )

    # Security configuration arguments
    security_group = parser.add_argument_group("Security Configuration")
    security_group.add_argument(
        "--allowed-commands", "-ac",
        type=str,
        help="Comma-separated list of commands that are allowed to be executed"
    )
    security_group.add_argument(
        "--allowed-paths", "-ap",
        type=str,
        help="Comma-separated list of paths that are allowed for command execution"
    )
    security_group.add_argument(
        "--commands-blacklist", "-cb",
        type=str,
        default="rm,mv,dd,mkfs,fdisk,format",
        help="Comma-separated list of commands that are not allowed (default: rm,mv,dd,mkfs,fdisk,format)"
    )
    security_group.add_argument(
        "--arguments-blacklist", "-ab",
        type=str,
        default="-rf,-fr,--force",
        help="Comma-separated list of arguments that are not allowed "
             "(default: -rf,-fr,--force)"
    )

    return parser.parse_args()


def update_environment_from_args(args):
    """Update environment variables from command-line arguments.

    Args:
        args (argparse.Namespace): Parsed command line arguments
    """
    env_mappings = {
        "ssh_host": "SSH_HOST",
        "ssh_port": "SSH_PORT",
        "ssh_username": "SSH_USERNAME",
        "allowed_commands": "SSH_ALLOWED_COMMANDS",
        "allowed_paths": "SSH_ALLOWED_PATHS",
        "commands_blacklist": "SSH_COMMANDS_BLACKLIST",
        "arguments_blacklist": "SSH_ARGUMENTS_BLACKLIST",
    }

    for arg_name, env_var in env_mappings.items():
        arg_value = getattr(args, arg_name, None)
        if arg_value is not None:
            os.environ[env_var] = str(arg_value)


def log_configuration():
    """Log the current server configuration."""
    # Use get() to safely access environment variables that might not be set
    config_vars = {
        "SSH host": os.environ.get('SSH_HOST', 'Not set'),
        "SSH port": os.environ.get('SSH_PORT', 'Not set'),
        "SSH username": os.environ.get('SSH_USERNAME', 'Not set'),
        "Allowed commands": os.environ.get('SSH_ALLOWED_COMMANDS', ''),
        "Allowed paths": os.environ.get('SSH_ALLOWED_PATHS', ''),
        "Commands blacklist": os.environ.get('SSH_COMMANDS_BLACKLIST', ''),
        "Arguments blacklist": os.environ.get('SSH_ARGUMENTS_BLACKLIST', ''),
    }

    logger.info("Starting SSH execution MCP server")

    for name, value in config_vars.items():
        logger.info(f"{name}: {value}")


def main():
    """Entry point for the SSH execution MCP server."""
    # Parse command line arguments
    args = parse_arguments()

    # Update environment variables from command-line arguments
    update_environment_from_args(args)

    # Log server configuration
    log_configuration()

    # Start the MCP server using the centralized function from server.py
    from .server import main as server_main
    server_main(transport="stdio")


if __name__ == "__main__":
    main()
