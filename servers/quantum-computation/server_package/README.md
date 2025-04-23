# Quantum Computation Server Package

This package is used to let quantum-computation MCP use quantum computation server to run gpaw calculations. Put this package on your computation server.

# Prerequisites

- python >= 3.12
- build-essential
- libblas-dev
- liblapack-dev
- libfftw3-dev
- libxc-dev
- libopenmpi-dev
- openmpi-bin

Consider using the following command to install all the prerequisites:

```bash
sudo apt install -y python3-pip python3-venv build-essential libblas-dev liblapack-dev \
                    libfftw3-dev libxc-dev libopenmpi-dev openmpi-bin
```

# Installation

```bash
uv pip install git+https://github.com/pathintegral-institute/mcp.science.git#subdirectory=servers/quantum_computation/src/server_package
```
