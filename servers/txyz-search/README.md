# TXYZ Search MCP Server
A Model Context Protocol (MCP) server for TXYZ Search API. Provides tools for academic and scholarly search, general web search, and smart search(automatically selects the best search type based on the query), user should register a TXYZ API key from [TXYZ Platform](https://platform.txyz.ai/console) before usage.

### Available Tools
- `txyz_search_scholar`: Academic and scholarly search for papers, articles, and other academic materials
- `txyz_search_web`: General web search functionality for resources from web pages
- `txyz_search_smart`: Automatically selects the best search type based on the query (may include either scholarly materials or web pages)

Each tool accepts the following parameters:
- `query`: The search query
- `max_results`: The maximum number of results to return (between 1 and 20)

## Prerequisites

- Python 3.10 or later (but less than 3.13)
- [uv](https://github.com/astral-sh/uv) - Python package installer and resolver
- TXYZ API key from [TXYZ Platform](https://platform.txyz.ai/console)

## Installation

### Using uv (recommended)

1. Install uv if you haven't already:
```bash
curl -sSf https://astral.sh/uv/install.sh | bash
```

2. Create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate
```

3. Install the package:
```bash
# For development installation
uv pip install -e .
```

When using `uv`, you can also use `uvx` to directly run `mcp-txyz-search` without explicit installation.

## Configuration

### Environment Variables

1. Copy the example environment file:
```bash
cp .env_example .env
```

2. Edit the `.env` file and add your TXYZ API key:
```
# TXYZ Search Env Variables
TXYZ_API_KEY="YOUR_TXYZ_API_KEY_HERE"
TXYZ_BASE_URL="https://api.txyz.ai/v1"
```

You can get your API key from the [TXYZ Platform Console](https://platform.txyz.ai/console).

### MCP Configuration

Add the following to your MCP configuration:
```json
{
  "mcpServers": {
    "mcp-txyz-search": {
      "command": "uvx",
      "args": [
        "mcp-txyz-search"
      ],
      "env": {
        "TXYZ_API_KEY": "YOUR_TXYZ_API_KEY_HERE"
      }
    }
  }
}
```

or Locally
```json
{
  "mcpServers": {
    "mcp-txyz-search": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/txyz-search",
        "mcp-txyz-search"
      ],
      "env": {
        "TXYZ_API_KEY": "YOUR_TXYZ_API_KEY_HERE"
      }
    }
  }
}
```

or Fetch and run from remote repository

```json
{
  "mcpServers": {
    "mcp-txyz-search": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/pathintegral-institute/mcp.science#subdirectory=servers/txyz-search",
        "mcp-txyz-search" 
      ],
      "env": {
        "TXYZ_API_KEY": "YOUR_TXYZ_API_KEY_HERE"
      }
    }
  }
}
```

## License
MIT
