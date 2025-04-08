# Quickstart

This guide will walk you through the process of setting up pre-built MCP servers locally.

## Prerequisites
- [MCPM](https://mcpm.sh/): a MCP manager developed by us, which is easy to use, open source, community-driven, forever free.
- [uv](https://docs.astral.sh/uv/): An extremely fast Python package and project manager, written in Rust. You can install it by running:
    ```bash
    curl -sSf https://astral.sh/uv/install.sh | bash
    ```
- MCP client: e.g. [Claude Desktop](https://claude.ai/download) / [Cursor](https://cursor.com) / [Windsurf](https://windsurf.com/editor) / [Chatwise](https://chatwise.app/) / [Cherry Studio](https://cherry-ai.com/)

## Integrate MCP servers into your client

MCP servers can be integrated with any compatible client application. Here, we'll walk through the integration process using the [`web-fetch`](../servers/web-fetch/) mcp server (included in this repository) as an example.


#### Client Integration

With MCPM, you can easily integrate MCP servers into your client application.

```bash
mcpm add web-fetch
```

You might need to restart your client application for the changes to take effect.


Then you can verify that the integration is working by asking to fetch web content:
   - "Can you fetch and summarize the content from https://modelcontextprotocol.io/?"
   - The `web-fetch` tool should be called and the content should be retrieved.
  

## Find other servers
We would recommend you to check [Available Servers](../docs/available_servers.md) or [MCPM Registry](https://mcpm.sh/registry/) for more servers.