# Jupyter Act MCP Server For AI Agents

Jupyter Act MCP Server is a Model Context Protocol (MCP) server that allows AI agents to interact with Jupyter environments, execute code, and retrieve results. This server provides a set of tools enabling AI to execute Python code in Jupyter Notebooks and return results in Jupyter Notebook compatible JSON format.

## Environment Setup

### Dependencies Installation

Before using the Jupyter Act MCP Server, install the following dependencies:

```bash
# Install Jupyter related dependencies
pip install jupyterlab jupyter-collaboration ipykernel
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
jupyter lab --ServerApp.port=${PORT} --IdentityProvider.token=${JUPYTER_SERVER_TOKEN}
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
    "jupyter-act": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/pathintegral-institute/mcp.science@main#subdirectory=servers/jupyter-act",
        "mcp-jupyter-act"
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

Jupyter Act MCP Server provides the following tools:

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

### 3. add_cell

Add a new cell to the specified notebook.

**Parameters**:
- `cell_type`: Cell type, should be 'code' or 'markdown' or 'raw'
- `notebook_path`: Relative path to the notebook file
- `cell_content`: The content to add to the cell

**Returns**:
- Cell added successfully

### 4. replace_cell

Replace the given cell in the notebook. ⚠️ **WARNING: This is a high-risk operation** that will modify the notebook content without user confirmation. Use with extreme caution and only when absolutely necessary.

**Parameters**:
- `notebook_path`: Relative path to the notebook file
- `cell_id_to_replace`: The id of the cell to replace
- `cell_content`: The Cell Content to replace

**Returns**:
- Cell replaced successfully

### 5. read_jupyter_file

Read file content. For regular files, returns the entire content; for .ipynb files, returns notebook cells in pages. Each read returns metadata containing cursor, has_more, and reverse values for subsequent reads.

**Parameters**:
- `file_path`: File path, supports both regular files and .ipynb files (relative path to the working directory)
- `cursor`: Starting position for reading, only applies to .ipynb files (default: 0). Use 0 for first read, then use the cursor value from previous read's metadata
- `cell_count`: Number of cells to read, only applies to .ipynb files (default: 10)
- `reverse`: Reading direction, only applies to .ipynb files (default: true). True means read from end to beginning, False means read from beginning to end

**Returns**:
- File content or notebook cell content with pagination metadata

### 6. list_jupyter_files

List files in the Jupyter workspace. To list files in the root directory, provide an empty string as file_path.

**Parameters**:
- `file_path`: Relative path to list files from (default: ""). Use empty string for root directory, or a path like 'subfolder/' for subdirectories

**Returns**:
- List of files and subdirectories in the directory

## Important Notes

1. Ensure the Jupyter server is running and accessible
2. Make sure environment variables are correctly configured
3. Before executing code, ensure the corresponding notebook is opened and with a kernel running
4. The `replace_cell` tool is a high-risk operation - use with extreme caution as it modifies notebook content without user confirmation
