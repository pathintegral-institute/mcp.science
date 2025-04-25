# Gpaw Computation Server Package

This package is used to let gpaw-computation MCP to run gpaw calculations. Put this package on your computation server.

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
                    libfftw3-dev libxc-dev libopenmpi-dev openmpi-bin git
```

# Installation

We would recommend you to create a working directory for virtual environment and install this package.

```bash
mkdir -p your-working-directory
cd your-working-directory
uv init
uv venv --python 3.12  # to make sure you use python 3.12
uv pip install git+https://github.com/pathintegral-institute/mcp.science.git#subdirectory=servers/gpaw-computation/server_package
```
