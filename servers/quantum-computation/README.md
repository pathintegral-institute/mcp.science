# Quantum Computation

# Prerequisites

- python >= 3.12
- uv
- mpi api key

# Computation server setup

the `server_package` folder contains scripts that is used to let quantum-computation MCP use quantum computation server to run gpaw calculations on your server, you need to install it on your server. Check the `server_package/README.md` for more details.

# Configure local MCP

before running the server, you need to configure the local MCP by checking `src/quantum_computation/config/settings.toml`

# Run the server

```bash
uv run mcp-quantum-computation
```
