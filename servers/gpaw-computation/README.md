# GPAW Computation

# Prerequisites

- python >= 3.12
- uv
  <details>
  <summary>How to install uv?</summary>

  For macOS and Linux:

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  For Windows:

  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
  ```

  </details>

- mpi api key
- material-project MCP: another helpful MCP Server for fetching structure data, please check https://github.com/pathintegral-institute/mcp.science/tree/main/servers/materials-project for more details.

# Computation server setup

the `server_package` folder contains scripts that is used to let gpaw-computation MCP to run gpaw calculations on your server, you need to install it on your server. Check the `server_package/README.md` for more details.

# Configure local MCP

before running the server, you need to configure the local MCP by checking `src/gpaw_computation/config/settings.toml`

Noted that `structure_cache_abs_path` is the output directory of materials-project MCP server

# Run the server

```bash
uv run mcp-gpaw-computation
```
