#!/usr/bin/env python3
"""
MCP Science Servers Launcher
"""

import sys
import subprocess
import click
from pathlib import Path

# First check if we're in development mode (servers are at project root level)
DEV_SERVERS_PATH = (Path(__file__).parent / '../../servers').resolve()
# Then check if we're in installed mode (servers would be in the package)
INSTALLED_SERVERS_PATH = (Path(__file__).parent / 'servers').resolve()

# Use the development path if it exists, otherwise use the installed path
SERVERS_PATH = DEV_SERVERS_PATH if DEV_SERVERS_PATH.exists() else INSTALLED_SERVERS_PATH
available_servers = [d.name for d in SERVERS_PATH.iterdir() if d.is_dir()] if SERVERS_PATH.exists() else []

@click.command(help="Launch an MCP server by name, installing optional dependencies first.\n\nAvailable servers: {}".format(', '.join(available_servers)))
@click.option('-b', '--branch', type=str, default=None, help='Branch to use for the MCP server', required=False)
@click.argument('server_name', type=str)
@click.argument('args', nargs=-1)
def main(server_name: str, branch: str | None = None, args: list[str] = []) -> None:
    """Launch an MCP server by name, installing optional dependencies first."""
    if branch is None:
        if server_name not in available_servers:
            raise click.BadParameter(
                f"server_name must be one of {available_servers} when --branch is not provided."
            )
        uvx_cmd = [
            "uvx",
            "--from", (SERVERS_PATH / server_name).resolve().as_posix(),
            f"mcp-{server_name}",
            *args,
        ]

    else:
        uvx_cmd = [
            "uvx",
            "--from", f"git+https://github.com/pathintegral-institute/mcp.science@{branch}#subdirectory=servers/{server_name}",
            f"mcp-{server_name}",
            *args,
        ]

    print(f"Running command: {uvx_cmd}")

    try:
        # Run the uvx command
        result = subprocess.run(uvx_cmd, check=False)
        sys.exit(result.returncode)

    except FileNotFoundError:
        print("Error: uvx command not found. Please install uv first.")
        sys.exit(1)
    except Exception as e:
        print(f"Error running {server_name}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()