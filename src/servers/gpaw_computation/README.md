# GPAW Computation

# Prerequisites

- python >= 3.12
- uv
  <details>
  <summary>How to install uv?</summary>

  For macOS and Linux:

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  For Windows:

  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
  ```

  </details>

- mpi api key
- material-project MCP: another helpful MCP Server for fetching structure data, please check https://github.com/pathintegral-institute/mcp.science/tree/main/servers/materials-project for more details.

# Computation server setup

the `server_package` folder contains scripts that is used to let gpaw-computation MCP to run gpaw calculations on your server, you need to install it on your server. Check the `server_package/README.md` for more details.

# Configure local MCP

before running the server, you need to configure the local MCP by checking `src/gpaw_computation/config/settings.toml`

Noted that `structure_cache_abs_path` is the output directory of materials-project MCP server

# Run the server

```bash
uv run mcp-gpaw-computation
```


## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><img src="https://api.dicebear.com/7.x/initials/svg?seed=Binghai%20Yan&?s=100" width="100px;" alt="Binghai Yan"/><br /><sub><b>Binghai Yan</b></sub><br /><a href="#ideas" title="Ideas, Planning, & Feedback">🤔</a> <a href="#research" title="Research">🔬</a> <a href="https://github.com/pathintegral-institute/gpaw-computation/commits?author=" title="Code">💻</a> <a href="https://github.com/pathintegral-institute/gpaw-computation/commits?author=" title="Tests">⚠️</a></td>
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

If you use the GPAW Computation MCP server in your research, please cite it as described in the [CITATION.cff](./CITATION.cff) file in this directory. For general repository citation, see the root [CITATION.cff](../../CITATION.cff).