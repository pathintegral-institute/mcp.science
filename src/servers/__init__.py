#!/usr/bin/env python3
"""
MCP Science Servers Launcher
"""

import sys
import subprocess
from typing import Optional


def main(server_name: Optional[str] = None) -> None:
    """Launch an MCP server by name, installing optional dependencies first."""
    if server_name is None:
        if len(sys.argv) < 2:
            print("Usage: mcp-science <server-name> [args...]")
            print("Available servers:")
            print("  example-server")
            print("  gpaw-computation")
            print("  jupyter-act")
            print("  materials-project")
            print("  mathematica-check")
            print("  nemad")
            print("  python-code-execution")
            print("  ssh-exec")
            print("  tinydb")
            print("  txyz-search")
            print("  web-fetch")
            print("\nThis is equivalent to: "
                  "uvx --from 'mcp-science[server-name]' server-name")
            sys.exit(1)
        server_name = sys.argv[1]

    # Map server names to their command names (some might be different)
    server_commands = {
        "example-server": "example-server",
        "gpaw-computation": "gpaw-computation",
        "jupyter-act": "jupyter-act",
        "materials-project": "materials-project",
        "mathematica-check": "mathematica-check",
        "nemad": "nemad",
        "python-code-execution": "python-code-execution",
        "ssh-exec": "ssh-exec",
        "tinydb": "tinydb",
        "txyz-search": "txyz-search",
        "web-fetch": "web-fetch",
    }

    if server_name not in server_commands:
        print(f"Unknown server: {server_name}")
        print("Available servers:", ", ".join(server_commands.keys()))
        sys.exit(1)

    command_name = server_commands[server_name]

    # Build the uvx command
    uvx_cmd = [
        "uvx",
        "--from", f"mcp.science[{server_name}]",
        command_name
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
