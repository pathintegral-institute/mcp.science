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
- [How to integrate MCP servers into LLM](#how-to-integrate-mcp-servers-into-llm)
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

Before installing the server, you need to specify the client you want to add the server to.

list available clients:

```bash
mcpm client ls
```

specify the client you want to add the server to:

```bash
mcpm client set <client-name>
```

then add the server:

```bash
mcpm add web-fetch
```

You may need to restart your client application for the changes to take effect.

Then you can validate whether the integration installed successfully by asking LLM to fetch web content:

- "Can you fetch and summarize the content from https://modelcontextprotocol.io/?"
- The `web-fetch` tool should be called and the content should be retrieved.

#### Find other servers

We would recommend you to check [Available Servers in this repo](#available-servers-in-this-repo) or [MCPM Registry](https://mcpm.sh/registry/) for more servers.

## How to build your own MCP server

Please check [How to build your own MCP server step by step](./docs/how-to-build-your-own-mcp-server-step-by-step.md) for more details.

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
   <details>
   <summary>👈 Click to see more conventions about directory and naming</summary>

   Please create your new server in the `servers` folder.
   For creating a new server folder under repository folder, you can simply run (replace `your-new-server` with your server name)

   ```sh
   uv init --package --no-workspace servers/your-new-server
   uv add --directory servers/your-new-server mcp
   ```

   This will create a new server folder with the necessary files:

   ```bash
   servers/your-new-server/
   ├── README.md
   ├── pyproject.toml
   └── src
       └── your_new_server
           └── __init__.py
   ```

   You may find there are 2 related names you might see in the config files:

   1. **Project name** (hyphenated): The folder, project name and script name in `pyproject.toml`, e.g. `your-new-server`.
   2. **Python package name** (snake_case): The folder inside `src/`, e.g. `your_new_server`.

   </details>

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
