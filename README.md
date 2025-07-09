<p align="center">
<img src="assets/logo_landscape.webp" width="800" />
</p>

<div align="center">

# MCP.science: Open Source MCP Servers for Scientific Research 🔍📚

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

_Join us in accelerating scientific discovery with AI and open-source tools!_

</div>

## Quick Start

Running any server in this repository is as simple as a single command. For example, to start the `web-fetch` server:

```bash
uvx mcp-science web-fetch
```

This command handles everything from installation to execution. For more details on configuration and finding other servers, see the "[How to configure MCP servers for AI client apps](#how-to-configure-mcp-servers-for-ai-client-apps)" section below.
## Table of Contents

- [About](#about)
- [What is MCP?](#what-is-mcp)
- [Available servers in this repo](#available-servers-in-this-repo)
- [How to integrate MCP servers into LLM](#how-to-integrate-mcp-servers-into-llm)
- [How to build your own MCP server](#how-to-build-your-own-mcp-server)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Citation](#citation)

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

Below is a complete list of the MCP servers that live in this monorepo.  Every
entry links to the sub-directory that contains the server’s source code and
README so that you can find documentation and usage instructions quickly.

#### [Example Server](./servers/example-server/)
An example MCP server that demonstrates the minimal pieces required for a
server implementation.

#### [Materials Project](./servers/materials-project/)
A specialised MCP server that enables AI assistants to search, visualise and
manipulate materials-science data from the Materials Project database.  A
Materials Project API key is required.

#### [Python Code Execution](./servers/python-code-execution/)
Runs Python code snippets in a secure, sandboxed environment with restricted
standard-library access so that assistants can carry out analysis and
computation without risking your system.

#### [SSH Exec](./servers/ssh-exec/)
Allows an assistant to run pre-validated commands on remote machines over SSH
with configurable authentication and command whitelists.

#### [Web Fetch](./servers/web-fetch/)
Fetches and processes HTML, PDF and plain-text content from the Web so that the
assistant can quote or summarise it.

#### [TXYZ Search](./servers/txyz-search/)
Performs Web, academic and “best effort” searches via the TXYZ API.  A TXYZ API
key is required.

#### [Timer](./servers/timer/)
A minimal countdown timer that streams progress updates to demonstrate MCP
notifications.

#### [GPAW Computation](./servers/gpaw-computation/)
Provides density-functional-theory (DFT) calculations through the GPAW package.

#### [Jupyter-Act](./servers/jupyter-act/)
Lets an assistant interact with a running Jupyter kernel, executing notebook
cells programmatically.

#### [Mathematica-Check](./servers/mathematica-check/)
Evaluates small snippets of Wolfram Language code through a headless
Mathematica instance.

#### [NEMAD](./servers/nemad/)
Neuroscience Model Analysis Dashboard server that exposes tools for inspecting
NEMAD data-sets.

#### [TinyDB](./servers/tinydb/)
Provides CRUD access to a lightweight JSON database backed by TinyDB so that an
assistant can store and retrieve small pieces of structured data.

## How to configure MCP servers for AI client apps

If you're not familiar with these stuff, here is a step-by-step guide for you: [Step-by-step guide to configure MCP servers for AI client apps](./docs/integrate-mcp-server-step-by-step.md)

### Prerequisites

1. [uv](https://docs.astral.sh/uv/) ­— a super-fast (Rust-powered) drop-in
   replacement for pip + virtualenv.  Install it with:

   ```bash
   curl -sSf https://astral.sh/uv/install.sh | bash
   ```

2. An MCP-enabled client application such as
   [Claude Desktop](https://claude.ai/download),
   [VSCode](https://code.visualstudio.com/),
   [Goose](https://block.github.io/goose/),
   [5ire](https://5ire.app/).

### The short version – use `uvx`

Any server in this repository can be launched with a single shell command.  The
pattern is:

```bash
uvx mcp-science <server-name>
```

For example, to start the `web-fetch` stdio server locally, configure the following command in your client:

```bash
uvx mcp-science web-fetch
```

Which corresponds to this in claude desktop's json configuration:
```json
{
  "mcpServers": {
    "web-fetch": {
      "command": "uvx",
      "args": [
        "mcp-science",
        "web-fetch"
      ]
    }
  }
}
```

The command will download the `mcp-science` package from PyPI and run the requested entry-point.

#### Find other servers

Have a look at the [Available servers](#available-servers-in-this-repo) list —
every entry in the table works with the pattern shown above.

---

### Optional: managing integrations with MCPM

[MCPM](https://mcpm.sh/) is a convenience command-line tool that can automate
the process of wiring servers into supported clients.  It is not required but
can be useful if you frequently switch between clients or maintain a large
number of servers.

The basic workflow is:

```bash
# Install mcpm first – it is a separate project
uv pip install mcpm

mcpm client ls           # discover supported clients
mcpm client set <name>   # pick the one you are using

# Add a server (automatically installing it if needed)
mcpm add web-fetch
```

After the command finishes, restart your client so that it reloads its tool
configuration.  You can browse the [MCPM Registry](https://mcpm.sh/registry/)
for additional community-maintained servers.

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

### Contributor Recognition in Subrepos

If you want to recognize contributors for a specific server/subrepo (e.g. `servers/gpaw-computation/`), you can use the [All Contributors CLI](https://allcontributors.org/docs/en/cli/installation) in that subdirectory.

**Steps:**

1. In your subrepo (e.g. `servers/gpaw-computation/`), create a `.all-contributorsrc` file (see [example](servers/gpaw-computation/.all-contributorsrc)).
2. Add contributors using the CLI:
   ```bash
   npx all-contributors add <github-username> <contribution-type>
   ```
3. Generate or update the contributors section in the subrepo's `README.md`:
   ```bash
   npx all-contributors generate
   ```
4. Commit the changes to the subrepo's `README.md` and `.all-contributorsrc`.

For more details, see the [All Contributors CLI installation guide](https://allcontributors.org/docs/en/cli/installation).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Thanks to all contributors!

## Citation

For general use, please cite this repository as described in the root [CITATION.cff](./CITATION.cff).

If you use a specific server/subproject, please see the corresponding `CITATION.cff` file in that subproject's folder under `servers/` for the appropriate citation.
