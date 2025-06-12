# NEMAD MCP Server

NEMAD (North East Materials Database) MCP server for accessing materials database through the NEMAD API.

## Features

- Search materials by elements in magnetic, thermoelectric, and superconductor databases
- Search materials by exact chemical formula
- Read specific ranges of search results
- Support for exact match and partial match searches

## Setup

1. Get a NEMAD API key:
   - Go to [nemad.org](https://nemad.org)
   - Create an account 
   - Generate an API key from your account dashboard

2. Install dependencies:
```bash
uv sync
```

3. Set your NEMAD API key as an environment variable:
```bash
export NEMAD_API_KEY="your-api-key"
```

## Usage

Add to your Claude Desktop config:

### Option 1: Local development
```json
{
  "mcpServers": {
    "nemad": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp.science/servers/nemad",
        "run",
        "mcp-nemad"
      ],
      "env": {
        "NEMAD_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Option 2: Direct from GitHub
```json
{
  "mcpServers": {
    "nemad": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/pathintegral-institute/mcp.science#subdirectory=servers/nemad",
        "mcp-nemad"
      ],
      "env": {
        "NEMAD_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Tools

- `nemad_search`: Search for materials by elements
- `nemad_formula_search`: Search for materials by exact chemical formula  
- `nemad_read_results`: Read specific range of cached search results