# Building Your Own MCP Server

## Introduction

Welcome, researchers! If you're here, you're likely interested in connecting your specialized scientific tools, analyses, or computational scripts with Large Language Models (LLMs) like Claude. This guide will help you transform your domain-specific code into powerful tools that LLMs can use to produce more accurate, contextualized, and useful outputs in your field.

### Benefits

By building your own MCP server, you can:
- **Improve accuracy**: LLMs can leverage your exact computational methods rather than approximating them
- **Enhance capabilities**: Extend what LLMs can do with your specialized tools
- **Maintain control**: Your code remains on your systems, with the LLM simply calling it when needed
- **Share expertise**: Make your specialized knowledge accessible through friendly conversational interfaces

### Prerequisites

Don't worry if you're not an experienced developer! This guide is designed to be accessible. You'll need:
- Basic familiarity with Python (enough to understand simple functions)
- Your existing research scripts or tools that you want to integrate
- Python installed on your computer

### What to expect

This guide will walk you through:
1. Setting up your development environment
2. Creating a basic MCP server structure
3. Integrating your existing scientific code
4. Testing your server with an LLM
5. Extending and improving your server

Each step includes detailed instructions and explanations. If you encounter any difficulties, remember that the MCP community is here to help!

Let's get started with creating your new server.

## Creating a new server

### 1. Initialize server package
Create a new server package using UV:

```sh
uv init --package --no-workspace servers/your-new-server
uv add --directory servers/your-new-server mcp
```
Be aware of the naming conventions: there are 3 different names for each MCP server:
1. the name of the code directory (the folder name and also the name defined in `project.name` of `pyproject.toml` in your server directory): use hyphen, e.g.:
    ```toml
    # servers/your-server/pyproject.toml
    [project]
    name = "your-server"
    ```
2. the name of the python package (the name of the directory in `servers/your-server/src`): use snake_case, e.g.: `servers/your-server/src/your_server`
3. the name of the script (defined in `[project.scripts]` section of `servers/your-server/pyproject.toml`): use snake_case and prefix with `mcp-` (**need to modify manually**), e.g.:
    ```toml
    [project.scripts]
    mcp-your-server = "your_server:main"
    ```


### 2. Implementing the simplest server
Let's implement a basic server that provides a simple addition tool first. Create or update `servers/your-new-server/src/your_new_server/__init__.py`:

```python
def main():
    from mcp.server.fastmcp import FastMCP
    import logging

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Initialize MCP server
    mcp = FastMCP()

    # Define your tools
    @mcp.tool()
    async def add(a: int, b: int) -> str:
        return str(a + b)

    # Start server
    logger.info('Starting your-new-server')
    mcp.run('stdio')
```

### 3. Launch server locally
Run your server using:

```sh
uv run --directory servers/your-new-server your-new-server
```

Upon successful startup, you should see output similar to:
```text
2025-04-01 10:22:36,402 - INFO - your_new_server - Starting your-new-server
```

### 4. Add more tools
You can add more tools to your server by defining new functions and decorating them with `@mcp.tool()`. For example:

```python
import numpy as np

@mcp.tool()
async def mean(a: int, b: int) -> str:
    return str(np.mean([a, b]))
```

More dependencies might be needed for your server, you can add them using `uv add` (the `pyproject.toml` will be updated automatically).

### 5. Test your server
run your MCP server locally and integrate it with a client.
take Claude Desktop as an example:

- Open Claude Desktop, find "Claude" -> "Settings"
- Enter "Developer" tab, click "Edit Config" to enter the directory of config file
- Add your server to the config file, e.g.:
```json
{
    // ...
    "mcpServers": {
        "your-new-server": {
            "command": "uv",
            "args": [
                "run",
                "--directory",
                "/path/to/your-new-server",
                "mcp-your-new-server"
            ]
        }
    }
}
```

### 6. Finish the README.md, commit the changes and create a pull request
Better README.md will make others easier to understand your server and use it.



### (Optional) 7. Add it to MCPM registry
To have your server easily accessible for others, you can add it to MCPM registry by following the [instructions](https://github.com/pathintegral-institute/mcpm.sh/blob/main/CONTRIBUTING.md) in MCPM registry.