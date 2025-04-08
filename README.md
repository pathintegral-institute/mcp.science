# MCP Servers
Open Source MCP (Message Control Protocol) Servers for Scientific Research

## Installation Options

### Option 1: Using PyPI Version
Install the latest stable version from PyPI using the following configuration:

```json
{
  "mcpServers": {
    "mcp-txyz-search": {
      "command": "uvx",
      "args": ["mcp-txyz-search"],
      "env": {
        "TXYZ_API_KEY": "YOUR_TXYZ_API_KEY_HERE"
      }
    }
  }
}
```

### Option 2: Using Latest Main Branch
For the most recent development version, use this configuration:

```json
{
  "mcpServers": {
    "mcp-txyz-search": {
      "command": "uvx",
      "args": [
        "--from", 
        "git+https://github.com/pathintegral-institute/mcp-servers#subdirectory=servers/txyz-search", 
        "mcp-txyz-search"
      ],
      "env": {
        "TXYZ_API_KEY": "YOUR_TXYZ_API_KEY_HERE"
      }
    }
  }
}
```

### Option 3: Using Specific Branch
To use a specific branch, modify the configuration as follows:

```json
{
  "mcpServers": {
    "mcp-txyz-search": {
      "command": "uvx",
      "args": [
        "--from", 
        "git+https://github.com/pathintegral-institute/mcp-servers@branch_name#subdirectory=servers/txyz-search", 
        "mcp-txyz-search"
      ],
      "env": {
        "TXYZ_API_KEY": "YOUR_TXYZ_API_KEY_HERE"
      }
    }
  }
}
```

## Creating a New Server

### 1. Initialize Server Package
Create a new server package using UV:

```sh
uv init --package --no-workspace servers/your-new-server
uv add --directory servers/your-new-server mcp
```

### 2. Configure Server
Create or update `servers/your-new-server/src/your_new_server/__init__.py`:

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

### 3. Launch Server
Run your server using:

```sh
uv run --directory servers/your-new-server your-new-server
```

Upon successful startup, you should see output similar to:
```text
2025-04-01 10:22:36,402 - INFO - your_new_server - Starting your-new-server
```

### Naming Conventions
There are 3 different names for each MCP server:
1. the name of the code directory (the folder name and also the name defined in `project.name` of `pyproject.toml` in your server directory): use hyphen, e.g.:
```toml
# servers/your-server/pyproject.toml
[project]
name = "your-server"
```
2. the name of the python package (the name of the directory in `servers/your-server/src`): use snake_case, e.g.: `servers/your-server/src/your_server`
3. the name of the script (defined in `[project.scripts]` section of `servers/your-server/pyproject.toml`): use snake_case and prefix with `mcp-`, e.g.:
```toml
[project.scripts]
mcp-your-server = "your_server:main"
```

## Contributing

We welcome contributions to MCP Servers! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your PR adheres to:
- Clear commit messages
- Proper documentation updates
- Test coverage for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors