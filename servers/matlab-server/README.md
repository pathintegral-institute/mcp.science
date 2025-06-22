# MATLAB MCP Server (Python)

This repository contains a Python-based Model Context Protocol (MCP) server that allows MCP clients (like Cursor or other AI agent environments) to execute MATLAB code and retrieve results, including plots.

## Overview

This server acts as a bridge, enabling applications that support MCP to leverage a local MATLAB installation for tasks such as:

*   Performing numerical computations and simulations.
*   Generating plots and visualizations from MATLAB.
*   Executing existing MATLAB scripts and functions.

The server interacts with MATLAB using the `matlab -batch` command-line interface.

## Prerequisites

*   **MATLAB Installation:** A licensed version of MATLAB must be installed on your system.
*   **`matlab` in PATH:** The `matlab` executable command must be available in your system's PATH. You can test this by running `matlab -help` or `matlab -batch "disp('hello'), exit"` in your terminal.
    *   On macOS, the path is typically `/Applications/MATLAB_R20XXx.app/bin/`.
    *   On Linux, it's usually `/usr/local/MATLAB/R20XXx/bin/`.
    *   On Windows, it's often `C:\Program Files\MATLAB\R20XXx\bin\`.
    Ensure the relevant directory is added to your system's PATH environment variable.
*   **Python:** Python >= 3.11 (as specified in `pyproject.toml`).
*   **`uv` (recommended):** For managing the Python environment (`pip` can also be used).

## Installation

1.  **Clone the repository (if you haven't already):**
    If you are working within a larger repository containing this server:
    ```bash
    # Navigate to the matlab-server directory
    cd path/to/your/clone/servers/matlab-server
    ```
    If obtaining it standalone (conceptual, as it's part of a larger structure):
    ```bash
    # git clone <repository-url>
    # cd <repository-directory>/servers/matlab-server
    ```

2.  **Set up the Python environment and install dependencies using `uv`:**
    ```bash
    # Create a virtual environment (from within servers/matlab-server)
    uv venv

    # Activate the environment
    # On macOS/Linux:
    source .venv/bin/activate
    # On Windows (Powershell):
    # .\.venv\Scripts\Activate.ps1
    # On Windows (CMD):
    # .\.venv\Scripts\activate.bat

    # Install dependencies (installs in editable mode using pyproject.toml)
    uv pip install -e .
    ```
    Alternatively, if not using editable mode or if you want to install it like a regular package (e.g., from a Git URL if it were published or directly accessible):
    ```bash
    # Example: uv pip install git+https://github.com/pathintegral-institute/mcp.science.git#subdirectory=servers/matlab-server
    ```


## Running the Server

To start the MCP server, ensure your virtual environment (where `mcp-matlab-server` was installed) is activated, and then run:

```bash
# Using the script defined in pyproject.toml
mcp-matlab-server
```

Or explicitly using the Python module:
```bash
python -m matlab_server.server
```

The server will start and listen for connections from MCP clients via standard input/output (stdio).

## Integration with MCP Clients (e.g., Cursor)

Follow the general steps for integrating MCP servers with your client:

1.  **Start the MATLAB MCP Server:** Run `mcp-matlab-server` in a terminal as described above.
2.  **Configure Your MCP Client:** Add the server to your client's configuration (e.g., `settings.json` for Cursor). You'll need to provide the command to run the server within its environment.

    Example configuration snippet for Cursor's `settings.json` (adjust paths as necessary):

    ```json
    {
      "mcpServers": {
        "matlab-server": {
          // Option 1: Running the installed script (ensure .venv/bin is in PATH or use absolute path)
          "command": "/path/to/your/project/servers/matlab-server/.venv/bin/mcp-matlab-server",
          // "disabled": false, // Uncomment to enable
          // "autoApprove": ["execute_matlab"] // Optional: auto-approve the tool
        }
        // ... other servers ...
      }
    }
    ```
    *Replace `/path/to/your/project/...` with the absolute path to the `mcp-matlab-server` executable within its virtual environment on your system.*

3.  **Restart Your MCP Client:** Ensure the client detects and loads the new server.

## Available Tools

The server exposes the following tool:

### 1. `execute_matlab`

Executes MATLAB code and returns the result.

**Input:**
*   `code` (string): MATLAB code to execute. This should be a self-contained script.
    *   If generating a plot, the code should produce a figure (e.g., using `plot()`, `surf()`, etc.). The server will attempt to save the *current* figure.
*   `output_format` (string, optional): Specifies the desired output format.
    *   `"text"` (default): Returns any text output (stdout) from the MATLAB script.
    *   `"plot"`: Attempts to save the current MATLAB figure as a PNG image and returns it as a base64 encoded string.

**Output:**
*   If `output_format` is `"text"`: `TextContent` containing the stdout from MATLAB.
*   If `output_format` is `"plot"`: `ImageContent` containing the base64 encoded PNG image, if a plot was successfully generated.
*   `ErrorContent`: If MATLAB is not found, the `matlab` command fails, the code is empty, or if `"plot"` is requested but no figure is generated or an error occurs during plotting.

**Important Considerations for `execute_matlab`:**
*   **Self-contained Code:** Each call to `execute_matlab` starts a new MATLAB session via `matlab -batch`. State (variables, workspace) is *not* preserved between calls.
*   **Plotting:** When `output_format` is `"plot"`, your MATLAB code should generate a figure. The server automatically adds commands to save the *current active figure*. If your code generates multiple figures, ensure the desired one is active before the script finishes. If no figure is generated, an error or warning will be indicated.
*   **MATLAB Errors:** Errors within your MATLAB script (e.g., syntax errors, runtime errors) will typically be captured and returned in the output or result in an `ErrorContent`. The server wraps the user's code in a basic `try...catch` block to help capture these.
*   **`exit` Command:** The server appends an `exit;` command to the MATLAB script to ensure the `matlab -batch` process terminates. You do not need to include `exit` in your provided code.

## Troubleshooting

*   **Server Not Found/Not Responding in Client:**
    *   Ensure the `mcp-matlab-server` is running in a terminal.
    *   Verify the Python virtual environment for the server is activated.
    *   Check if `matlab` is correctly installed and its `bin` directory is in your system's PATH. Test with `matlab -batch "disp('test'), exit;"` in a new terminal.
    *   Double-check the `command` path in your MCP client's configuration. It must point to the `mcp-matlab-server` executable *within its correct virtual environment*.
*   **Tool Errors (`execute_matlab`):**
    *   Check the server's terminal output for logs and specific error messages from MATLAB.
    *   Verify the syntax of your MATLAB `code`.
    *   If requesting a plot, ensure your code actually generates a figure.
    *   If MATLAB itself crashes or exits with an error code, the server will report this.
*   **Python/Dependency Issues:** Ensure dependencies are installed correctly in the virtual environment using `uv pip install -e .` within the `servers/matlab-server` directory.
*   **MATLAB Licensing Issues:** `matlab -batch` may fail or hang if there are MATLAB licensing problems. Ensure your MATLAB license is active and configured correctly for command-line use.

## Project Structure

*   `src/matlab_server/`: Python source code for the server.
    *   `server.py`: Main server logic, MCP tool definitions, and MATLAB interaction.
*   `pyproject.toml`: Project metadata and dependencies.
*   `setup.py`: Additional build and packaging information.
*   `.python-version`: Specifies the Python version (e.g., for `pyenv`).
*   `README.md`: This file.
*   `uv.lock`: (Generated by `uv`) Lockfile for dependencies.
```
