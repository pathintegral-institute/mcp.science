# Jupyter MCP Server For AI Agents

Jupyter MCP Server is a Model Context Protocol (MCP) server that allows AI agents to interact with Jupyter environments, execute code, and retrieve results. This server provides a set of tools enabling AI to execute Python code in Jupyter Notebooks and return results in Jupyter Notebook compatible JSON format.

## Environment Setup

### Dependencies Installation

Before using the Jupyter MCP Server, install the following dependencies:

```bash
# Install Jupyter related dependencies
pip install jupyterlab==4.4.1 jupyter-collaboration==4.0.2 ipykernel
```

### Environment Variables Configuration

Jupyter MCP Server requires the following environment variables to function properly:

```bash
# Jupyter server URL in the format {schema}://{host}:{port}/{base_url}
export JUPYTER_SERVER_URL="http://localhost:port"

# Jupyter server access token
export JUPYTER_SERVER_TOKEN="your_jupyter_token"

# Optional: Execution wait timeout in seconds, default is 60 seconds
export WAIT_EXECUTION_TIMEOUT=60
```

## Starting Jupyter Environment
### Starting from Local
1. Start the Jupyter Lab server:

```bash
jupyter lab --ServerApp.port=${PORT} --ServerApp.token=${JUPYTER_SERVER_TOKEN}
```

2. Note the access token generated, which will be displayed in the terminal output in the format:
   ```
   http://localhost:port/lab?token=your_jupyter_token
   ```

3. Set this token as the `JUPYTER_SERVER_TOKEN` environment variable.

### Using remote server Alternatively
or you can use a remote jupyter server, just set the `JUPYTER_SERVER_URL` environment variable to the remote server URL and `JUPYTER_SERVER_TOKEN` to the remote server token.

## Configuring MCP Server

Use the `uvx` command-line tool to install and start the MCP Server:

```json
{
  "mcpServers": {
    "jupyter-code-execution": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/pathintegral-institute/mcp.science.git#subdirectory=servers/jupyter-code-execution",
        "mcp-jupyter-code-execution"
      ],
      "env": {
        "JUPYTER_SERVER_URL": "${JUPYTER_SERVER_URL}",
        "JUPYTER_SERVER_TOKEN": "${JUPYTER_SERVER_TOKEN}"
      }
    }
  }
}
```

## Tools Description

Jupyter MCP Server provides the following tools:

### 1. execute_code

Execute code in a specified notebook.

**Parameters**:
- `notebook_path`: Relative path to the notebook file
- `code`: Code to execute

**Returns**:
- Execution results, including standard output, error messages, execution results, etc.

### 2. add_cell_and_execute_code

Add a new code cell to the specified notebook and execute it.

**Parameters**:
- `notebook_path`: Relative path to the notebook file
- `code`: Code to execute

**Returns**:
- Execution results, including standard output, error messages, execution results, etc.

### 3. read_file_from_jupyter_workdir

Read file content. For regular files, returns the entire content; for .ipynb files, returns notebook cells in pages.

**Parameters**:
- `file_path`: File path, supports both regular files and .ipynb files
- `cursor`: Starting position, only applies to .ipynb files
- `cell_count`: Number of cells to read, only applies to .ipynb files
- `reverse`: Reading direction, only applies to .ipynb files

**Returns**:
- File content or notebook cell content

### 4. list_files_from_jupyter_workdir

List files in the specified directory.

**Parameters**:
- `file_path`: Relative path to the working directory

**Returns**:
- List of files and subdirectories in the directory

### 5. list_root_files_from_jupyter_workdir

List files in the Jupyter root directory.

**Parameters**:
- None

**Returns**:
- List of files and subdirectories in the root directory

## Important Notes

1. Ensure the Jupyter server is running and accessible
2. Make sure environment variables are correctly configured
3. Before executing code, ensure the corresponding notebook is opened and with a kernel running
