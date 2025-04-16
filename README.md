<p align="center">
<img src="assets/logo_landscape.webp" width="800" />
</p>

<div align="center">

# MCP.science: Open Source MCP Servers for Scientific Research 🔍📚

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

_Join us in accelerating scientific discovery with AI and open-source tools!_

</div>

## Table of Contents

- [About](#about)
- [What is MCP?](#what-is-mcp)
- [Available servers in this repo](#available-servers-in-this-repo)
- [How to integrate MCP servers into your client](#how-to-integrate-mcp-servers-into-your-client)
- [How to build your own MCP server](#how-to-build-your-own-mcp-server)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## About

This repository contains a collection of open source [MCP](https://modelcontextprotocol.io/introduction) servers specifically designed for scientific research applications. These servers enable Al models (like Claude) to interact with scientific data, tools, and resources through a standardized protocol.

## What is MCP?

> MCP is an open protocol that standardizes how applications provide context to LLMs. Think of MCP like a USB-C port for AI applications. Just as USB-C provides a standardized way to connect your devices to various peripherals and accessories, MCP provides a standardized way to connect AI models to different data sources and tools.
>
> MCP helps you build agents and complex workflows on top of LLMs. LLMs frequently need to integrate with data and tools, and MCP provides:
>
> - A growing list of pre-built integrations that your LLM can directly plug into
> - The flexibility to switch between LLM providers and vendors
> - Best practices for securing your data within your infrastructure
>
> Source: [https://modelcontextprotocol.io/introduction](https://modelcontextprotocol.io/introduction)

## Available servers in this repo

#### [Example Server](./servers/example-server/)

A example mcp server that help understand how mcp server works.

#### [Materials Project](./servers/materials-project/)

A specialized mcp server that enables Al assistants to search, visualize, and manipulate materials science data from the Materials Project database. A Materials Project API key is required.

#### [Python Code Execution](./servers/python-code-execution/)

A secure sandboxed environment that allows AI assistants to execute Python code snippets with controlled access to standard library modules, enabling data analysis and computation tasks without security risks.

#### [SSH Exec](./servers/ssh-exec/)

A specialized mcp server that enables AI assistants to securely run validated commands on remote systems via SSH, with configurable restrictions and authentication options.

#### [Web Fetch](./servers/web-fetch/)

A versatile mcp server that allows AI assistants to fetch and process HTML, PDF, and plain text content from websites, enabling information gathering from online sources.

#### [TXYZ Search](./servers/txyz-search/)

A specialized mcp server that enables AI assistants to perform academic and scholarly searches, general web searches, or automatically select the best search type based on the query. A TXYZ API key is required.

## How to integrate MCP servers into LLM

If you're not familiar with these stuff, here is a step-by-step guide for you: [Step-by-step guide to integrate MCP servers into LLM](./docs/integrate-mcp-server-step-by-step.md)

### Prerequisites

- [MCPM](https://mcpm.sh/): a MCP manager developed by us, which is easy to use, open source, community-driven, forever free.
- [uv](https://docs.astral.sh/uv/): An extremely fast Python package and project manager, written in Rust. You can install it by running:
  ```bash
  curl -sSf https://astral.sh/uv/install.sh | bash
  ```
- MCP client: e.g. [Claude Desktop](https://claude.ai/download) / [Cursor](https://cursor.com) / [Windsurf](https://windsurf.com/editor) / [Chatwise](https://chatwise.app/) / [Cherry Studio](https://cherry-ai.com/)

### Integrate MCP servers into your client

MCP servers can be integrated with any compatible client application. Here, we'll walk through the integration process using the [`web-fetch`](./servers/web-fetch/) mcp server (included in this repository) as an example.

#### Client Integration

With MCPM, you can easily integrate MCP servers into your client application.

```bash
mcpm add web-fetch
```

The `mcpm` will automatically add the server to your client application, you can also specify the client you want to add the server to.

You might need to restart your client application for the changes to take effect.

Then you can verify that the integration is working by asking to fetch web content:

- "Can you fetch and summarize the content from https://modelcontextprotocol.io/?"
- The `web-fetch` tool should be called and the content should be retrieved.

#### Find other servers

We would recommend you to check [Available Servers in this repo](#available-servers-in-this-repo) or [MCPM Registry](https://mcpm.sh/registry/) for more servers.

## How to build your own MCP server

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

### Steps to create a new server

#### 1. Initialize server package

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

#### 2. Implementing the simplest server

Let's implement a basic server that provides a simple addition tool first. Create or update `servers/your-new-server/src/your_new_server/__init__.py`:

```python
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


def main():
    # Start server
    logger.info('Starting your-new-server')
    mcp.run('stdio')
```

#### 3. Launch server locally

Run your server using:

```sh
uv run --directory servers/your-new-server your-new-server
```

Upon successful startup, you should see output similar to:

```text
2025-04-01 09:58:42,666 - INFO - your_new_server - Starting your-new-server
```

#### 4. Add more tools

You can add more tools to your server by defining new functions and decorating them with `@mcp.tool()`. For example:

```python
import numpy as np

@mcp.tool()
async def mean(a: int, b: int) -> str:
    return str(np.mean([a, b]))

...
```

More dependencies might be needed for your server, you can add them using `uv add` (the `pyproject.toml` will be updated automatically).

#### 5. Test your server

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

Alternatively, you can use `mcpm inspector` to check your MCP server implementation through [mcp inspector](https://github.com/modelcontextprotocol/inspector). The inspector will launch a web interface where you can test and debug MCP servers.

#### 6. Finish the README.md, commit the changes and create a pull request

Better README.md will make others easier to understand your server and use it.

#### (Optional) 7. Add it to MCPM registry

To have your server easily accessible for others, you can add it to MCPM registry by following the [instructions](https://github.com/pathintegral-institute/mcpm.sh/blob/main/CONTRIBUTING.md) in MCPM registry.

## Contributing

We enthusiastically welcome contributions to MCP.science! You can help with improving the existing servers, adding new servers, or anything that you think will make this project better.

If you are not familiar with GitHub and how to contribute to a open source repository, then it might be a bit of challenging, but it's still easy for you. We would recommend you to read these first:

- [How to make your first pull request on GitHub](https://www.freecodecamp.org/news/how-to-make-your-first-pull-request-on-github-3/)
- [Creating a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request?tool=webui)

In short, you can follow these steps:

1. Fork the repository to your own GitHub account
2. Clone the forked repository to your local machine
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Make your changes and commit them (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

Please make sure your PR adheres to:

- Clear commit messages
- Proper documentation updates
- Test coverage for new features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Thanks to all contributors!
