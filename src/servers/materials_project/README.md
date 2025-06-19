# Materials Project MCP Server

A MCP (Model Context Protocol) server that interacts with the Materials Project database, allowing for material search, structure visualization, and manipulation.

## Overview

This MCP server provides tools to:

- Search for materials by chemical formula
- Retrieve and visualize crystal structures
- Generate and manipulate supercells
- Create moiré structures for 2D materials

## Tools

### `search_materials_by_formula`

Search for materials in the Materials Project database by chemical formula.

**Parameters:**
- `chemical_formula` (string): The chemical formula of the material

**Returns:**
- A list of text descriptions for structures matching the given formula

### `select_material_by_id`

Select a specific material by its material ID.

**Parameters:**
- `material_id` (string): The ID of the material

**Returns:**
- A list of TextContent objects containing the structure description and URI

### `get_structure_data`

Retrieve structure data in specified format.

**Parameters:**
- `structure_uri` (string): The URI of the structure
- `format` (string, optional): Output format, either "cif" or "poscar" (default: "poscar")

**Returns:**
- The structure file content as a string

### `create_structure_from_poscar`

Create a new structure from a POSCAR string.

**Parameters:**
- `poscar_str` (string): The POSCAR string of the structure

**Returns:**
- Information about the newly created structure, including its URI

### `plot_structure`

Visualize the crystal structure.

**Parameters:**
- `structure_uri` (string): The URI of the structure
- `duplication` (list of 3 integers, optional): The duplication of the structure along a, b, c axes (default: [1, 1, 1])

**Returns:**
- A PNG image of the structure and a Plotly JSON representation

### `build_supercell`

Create a supercell from a bulk structure.

**Parameters:**
- `bulk_structure_uri` (string): The URI of the bulk structure
- `supercell_parameters` (SupercellParameters): Parameters defining the supercell

**Returns:**
- Information about the newly created supercell structure

### `moire_homobilayer`

Generate a moiré superstructure of a 2D homobilayer.

**Parameters:**
- `bulk_structure_uri` (string): The URI of the bulk structure
- `interlayer_spacing` (float): The interlayer spacing between the two layers in Ångström
- `max_num_atoms` (int, optional): Maximum number of atoms in the moiré superstructure (default: 10)
- `twist_angle` (float, optional): Twist angle in degrees (default: 0.0)
- `vacuum_thickness` (float, optional): Vacuum thickness in z-direction in Ångström (default: 15.0)

**Returns:**
- Information about the newly created moiré structure

## Setup

### Materials Project API Key

To use this server, you need to obtain an API key from the Materials Project:

1. Register for an account at [Materials Project](https://materialsproject.org/)
2. Once logged in, go to your Dashboard
3. Navigate to the API Keys section and generate a new key

### Running as an MCP Server

This server is designed to be used with the MCP (Model Context Protocol) framework, which allows Large Language Models to interact with external tools.

#### Installation

(Navigate to the root folder of your local clone before taking the following steps.)

##### Using `uv` (Recommended)

[`uv`](https://github.com/astral-sh/uv) is a fast, reliable Python package installer and resolver. It's recommended for managing dependencies:

```bash
# Create a Python environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv sync
```

#### Configuration

Depending on which MCP client you're using, you'll need to configure it to use this server:

**For Claude Desktop:**

Edit your Claude Desktop config file (typically at `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

##### Using Local Directory (Current Method)

```json
{
  "mcpServers": {
    "materials_project": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-servers/servers/materials_project/",
        "run",
        "mcp-materials-project"
      ],
      "env": {
        "MP_API_KEY": "your_materials_project_api_key_here"
      }
    }
  }
}
```

##### Using PyPI Package (Future Method)

In the future, if/when a PyPI package becomes available, you can simplify installation and configuration:

```json
{
  "mcpServers": {
    "materials_project": {
      "command": "uvx",
      "args": [
        "mcp_materials_project"
      ],
      "env": {
        "MP_API_KEY": "your_materials_project_api_key_here"
      }
    }
  }
}
```

or Fetch and run from remote repository

```json
{
  "mcpServers": {
    "materials_project": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/pathintegral-institute/mcp.science#subdirectory=servers/materials-project",
        "mcp-materials-project"
      ],
      "env": {
        "MP_API_KEY": "YOUR_MP_API_KEY"
      }
    }
  }
}
```

**For Other MCP Clients:**

For other MCP clients like MCP CLI or custom implementations, refer to their specific documentation for how to register an MCP server. You'll always need to ensure the `MP_API_KEY` environment variable is properly set for the server process.


## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><img src="https://api.dicebear.com/7.x/initials/svg?seed=Binghai%20Yan&?s=100" width="100px;" alt="Binghai Yan"/><br /><sub><b>Binghai Yan</b></sub><br /><a href="#ideas" title="Ideas, Planning, & Feedback">🤔</a> <a href="#research" title="Research">🔬</a> <a href="https://github.com/pathintegral-institute/materials-project/commits?author=" title="Code">💻</a> <a href="https://github.com/pathintegral-institute/materials-project/commits?author=" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><img src="https://api.dicebear.com/7.x/initials/svg?seed=Yanzhen%20Wang&?s=100" width="100px;" alt="Yanzhen Wang"/><br /><sub><b>Yanzhen Wang</b></sub><br /><a href="#ideas" title="Ideas, Planning, & Feedback">🤔</a> <a href="#research" title="Research">🔬</a> <a href="https://github.com/pathintegral-institute/materials-project/commits?author=" title="Code">💻</a> <a href="https://github.com/pathintegral-institute/materials-project/commits?author=" title="Tests">⚠️</a></td>
    </tr>
  </tbody>
  <tfoot>
    <tr>
      <td align="center" size="13px" colspan="7">
        <img src="https://raw.githubusercontent.com/all-contributors/all-contributors-cli/1b8533af435da9854653492b1327a23a4dbd0a10/assets/logo-small.svg">
          <a href="https://all-contributors.js.org/docs/en/bot/usage">Add your contributions</a>
        </img>
      </td>
    </tr>
  </tfoot>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## 📖 Citation

If you use the Materials Project MCP server in your research, please cite it as described in the [CITATION.cff](./CITATION.cff) file in this directory. For general repository citation, see the root [CITATION.cff](../../CITATION.cff).