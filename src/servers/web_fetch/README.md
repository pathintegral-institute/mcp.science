# MCP-Web-Fetch
A Model Context Protocol (MCP) server for fetching webpages including html/pdf/plain text type content.

## Available Tools
- `fetch-web`: Fetch URL and return content according to its content type.
  - `url`: URL to fetch
  - `raw`: Whether to return raw content

## Installation
### Using uv(recommended)
When using `uv`, no specific installation is needed. We will use `uvx` to directly run `mcp-web-fetch`.

### Using pip
```bash
pip install mcp-web-fetch
```
After installation, you can run the server using
```bash
python -m mcp-web-fetch
```

## Configuration
Add to your local client
```json
{
    "mcpServers": {
        "mcp-web-fetch": {
            "command": "uvx",
            "args": ["mcp-web-fetch"]
        }
    }
}
```
or using docker(after publish done)
```json
{
    "mcpServers": {
        "mcp-web-fetch": {
            "command": "docker",
            "args": [
                "run",
                "-i",
                "--rm",
                "ghcr.io/mcp-servers/fetch:latest"
            ]
        }
    }
}
```

or Fetch and run from remote repository

```json
{
  "mcpServers": {
    "mcp-web-fetch": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/pathintegral-institute/mcp.science#subdirectory=servers/web-fetch",
        "mcp-web-fetch"
      ]
    }
  }
}
```

## Customization
By default, the server will use a default user-agent for fetching web content. You can customize the user-agent by setting the `user_agent` in args
```
uvx mcp-web-fetch --user-agent "Your User-Agent"
```
