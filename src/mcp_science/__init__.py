#!/usr/bin/env python3
"""
MCP Science Servers Launcher
"""

import sys
import subprocess
import click

available_servers = [
    "example-server",
    "gpaw-computation",
    "jupyter-act",
    "materials-project",
    "mathematica-check",
    "nemad",
    "python-code-execution",
    "ssh-exec",
    "tinydb",
    "txyz-search",
    "web-fetch",
]

@click.command()
@click.argument(
    'server_name',
    type=click.Choice(available_servers),
)
@click.option(
    '-b',
    '--branch',
    type=str,
    default='main',
    help='Branch to use for the MCP server',
    required=False,
)
def main(server_name: str, branch: str = "main") -> None:
    """Launch an MCP server by name, installing optional dependencies first."""

    # Build the uvx command
    uvx_cmd = [
        "uvx",
        "--from", f"git+https://github.com/pathintegral-institute/mcp.science@{branch}#subdirectory=servers/{server_name}",
        f"mcp-{server_name}",
    ]
    print(f"Running command: {uvx_cmd}")

    # Add any additional arguments
    if len(sys.argv) > 2:
        uvx_cmd.extend(sys.argv[2:])

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