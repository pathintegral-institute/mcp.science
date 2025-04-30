# Mathematica MCP Server (Python)

This repository contains a Python-based Model Context Protocol (MCP) server that allows MCP clients (like Cursor) to execute Mathematica code via `wolframscript` and verify mathematical derivations.

This is a Python port of the original TypeScript server.

## Overview

This server acts as a bridge, enabling applications that support MCP to leverage the power of a local Mathematica installation for tasks such as:

*   Performing complex mathematical calculations.
*   Verifying mathematical derivation steps provided by humans or AI models.
*   Generating LaTeX or Mathematica string representations of expressions.

## Prerequisites

*   [Mathematica](https://www.wolfram.com/mathematica/) must be installed on your system.
*   The `wolframscript` command-line utility must be available in your system's PATH. You can test this by running `wolframscript -help` in your terminal.
*   [Python](https://www.python.org/) >= 3.12.
*   [`uv`](https://github.com/astral-sh/uv) (recommended for managing the Python environment).

## Installation

### Directly way
```bash
uvx --from git+https://github.com/pathintegral-institute/mcp.science.git#subdirectory=servers/mathematica-check mcp-mathematica-check
```


### Clone codes to local and use

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd <repository-directory>/servers/mathematica-check
    ```
2.  **Set up the Python environment and install dependencies using `uv`:**

    ```bash
    # Create a virtual environment
    uv venv

    # Activate the environment
    # On macOS/Linux:
    source .venv/bin/activate
    # On Windows (Powershell):
    # .venv\Scripts\activate

    # Install dependencies
    uv pip install -e . # Installs in editable mode using pyproject.toml
    ```

## Running the Server

To start the MCP server, ensure your virtual environment is activated, and then run:

```bash
# Using the script defined in pyproject.toml
mcp-mathematica-check
```

Or explicitly:

```bash
python -m mathematica_check.server
```

Or using the MCP CLI:

```bash
mcp run src/mathematica_check/server.py
```

The server will start and listen for connections from MCP clients via standard input/output (stdio).

## Integration with MCP Clients (e.g., Cursor)

Follow the general steps for integrating MCP servers with your client:

1.  **Start the Mathematica MCP Server:** Run the server in a terminal as described above.
2.  **Configure Your MCP Client:** Add the server to your client's configuration (e.g., `settings.json` or similar). You'll need to provide the command to run the server within its environment.

    Example configuration snippet:

    ```json
    {
      "mcpServers": {
        "mathematica-check": {
          // Option 1: Running the installed script (ensure .venv/bin is in PATH or use absolute path)
          "command": "/path/to/your/project/servers/mathematica-check/.venv/bin/mcp-mathematica-check",

          // Option 2: Explicitly using python from the venv
          // "command": "/path/to/your/project/servers/mathematica-check/.venv/bin/python",
          // "args": ["-m", "mathematica_check.server"],
          // "cwd": "/path/to/your/project/servers/mathematica-check", // Set working directory to the root of mathematica-check

          "disabled": false,
          "autoApprove": [] // Optional: Add tool names ("execute_mathematica", "verify_derivation")
        }
        // ... other servers ...
      }
    }
    ```
    *Replace `/path/to/your/project/...` with the absolute paths on your system.* Ensure the client can execute the command within the correct virtual environment.

3.  **Restart Your MCP Client:** Ensure the client detects the new server.

## Available Tools

The server exposes the same tools as the TypeScript version:

### 1. `execute_mathematica`

Executes arbitrary Mathematica code.

**Input:**
*   `code` (string): Mathematica code to execute.
*   `format` (string, optional): Output format (`text`, `latex`, `mathematica`). Default: `text`.

**Output:** `TextContent` or `ErrorContent`.

### 2. `verify_derivation`

Verifies a sequence of mathematical expressions.

**Input:**
*   `steps` (list[string]): List of expressions (at least two).
*   `format` (string, optional): Output format for the report (`text`, `latex`, `mathematica`). Default: `text`.

**Output:** `TextContent` or `ErrorContent`.

## Troubleshooting

*   **Server Not Found/Not Responding:**
    *   Ensure the server is running (`mathematica-check` or `python -m mathematica-check.server`).
    *   Verify the virtual environment is activated.
    *   Check if `wolframscript` is installed and in your PATH (`wolframscript -help`).
    *   Check the client's MCP configuration, especially the `command`, `args`, and `cwd`.
*   **Tool Errors:**
    *   Check the server's terminal output for logs and errors.
    *   Verify the syntax of the Mathematica `code` or `steps`.
    *   Ensure `steps` for `verify_derivation` is a list with at least two strings.
*   **Python/Dependency Issues:** Ensure dependencies are installed correctly in the virtual environment using `uv pip install -e .`.

## Project Structure

*   `src/mathematica_check`: Python source code for the server.
    *   `server.py`: Main server logic and tool definitions.
*   `pyproject.toml`: Project metadata and dependencies (for `uv` and `pip`).
*   `.python-version`: Specifies the required Python version (used by tools like `pyenv`).
*   `README.md`: This file.
*   `uv.lock`: (Generated by `uv`) Lockfile for dependencies. 
