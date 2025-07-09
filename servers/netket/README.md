# NetKet MCP Server

A Model Context Protocol (MCP) server for quantum many-body physics analysis using [NetKet](https://www.netket.org/). This server provides natural language tools for creating, analyzing, and visualizing quantum systems.

> **Built on NetKet**: This MCP server leverages [NetKet](https://www.netket.org/), the machine-learning toolbox for quantum physics, to provide accessible quantum many-body analysis through natural language interfaces.

## What It Does

The NetKet MCP server enables you to:
- **Create quantum systems** using natural language descriptions
- **Analyze energy spectra** and phase transitions  
- **Perform parameter sweeps** to study quantum phases
- **Generate visualizations** of results automatically
- **Manage complex workflows** with persistent state


## Usage Examples

### Basic Quantum System Analysis

```
"Analyze the SSH model for a 24-site chain with t1=1.0 and t2=0.2"
```

This will:
1. Create a new quantum system
2. Set up a 24-site chain lattice
3. Configure the Hilbert space for 1 spinless fermion
4. Build the SSH Hamiltonian with specified parameters
5. Compute the energy spectrum
6. Analyze edge states and localization
7. Generate visualization plots

### Parameter Sweeps

```
"Study the SSH phase transition by sweeping t2 from 0.1 to 2.0 while keeping t1=1.0"
```

This performs a parameter sweep to identify quantum phase transitions.

### Custom Analysis

```
"Create a 4x4 square lattice with spin-1/2 particles and analyze the Heisenberg model with J=1.0"
```

Natural language descriptions are converted to precise quantum system specifications.

## Current Support Matrix

The MCP server currently supports flexible combinations of lattices, particle types, and Hamiltonian models:

### Lattice Geometries
- **1D**: Chain
- **2D**: Square, triangular, kagome, honeycomb  
- **3D**: Cube, FCC, BCC, pyrochlore
- **Higher-D**: Hypercube

### Particle Types (Hilbert Spaces)
- **Spins**: Configurable spin values (spin-1/2, spin-1, etc.)
- **Fermions**: Spinless or with spin, fixed particle number
- **Bosons**: Fixed particle number, configurable modes

### Hamiltonian Models
- **SSH Model** (`t1`, `t2`): Su-Schrieffer-Heeger chain for topological phases
- **Hubbard Model** (`t`, `U`): Fermionic systems with on-site interactions  
- **Fermion Hopping** (`t`, `B`): General fermionic hopping with magnetic field
- **Heisenberg Model** (`J`): Spin systems with exchange interactions
- **Ising Model** (`Jz`, `hx`, `hz`): Spin systems with Ising interactions
- **Kitaev Model** (`Jx`, `Jy`, `Jz`): Anisotropic spin interactions

### Compatible Combinations
- **Fermionic models** (SSH, Hubbard, Fermion Hopping) work with fermion Hilbert spaces
- **Spin models** (Heisenberg, Ising, Kitaev) work with spin Hilbert spaces  
- **All lattice geometries** are compatible with all particle types
- **Parameter sweeps** are supported for any model parameter

## Analysis Capabilities

- **Energy Spectra**: Exact diagonalization for eigenvalues and eigenvectors
- **Ground State Properties**: Correlation functions, order parameters
- **Parameter Sweeps**: Automated exploration of phase diagrams  
- **Localization Analysis**: Edge states, Anderson localization
- **Visualization**: Automatic plot generation and display

## Natural Language Interface

The server uses natural language processing to convert descriptions into structured quantum objects:

| Description | Result |
|-------------|---------|
| "24-site chain" | 1D lattice with 24 sites |
| "1 spinless fermion" | Fermionic Hilbert space, N=1 |
| "SSH model with t1=1, t2=0.2" | SSH Hamiltonian with specified hopping |
| "4x4 square lattice" | 2D square lattice, 16 sites |
| "spin-1/2 on each site" | Spin-1/2 Hilbert space |

## Output and Results

All analysis results are automatically saved with organized file structure:
- **Energy spectra**: Eigenvalues and eigenvectors
- **Plots**: High-quality visualizations (PNG format)
- **Data**: Numerical results in accessible formats
- **Metadata**: System parameters and analysis history

Results are stored in `/tmp/quantum_systems/` with unique system IDs for easy retrieval.


## Development and Contributing

This NetKet MCP server is built using a **self-evolving framework** that continuously improves through iterative testing against scientific computing tasks. The tools grow and adapt based on real-world usage patterns rather than manual optimization.

### For Contributors and Developers
- **Framework Architecture**: Learn about the self-evolution loop, memory management, and natural language parsing
- **Contributing Guide**: Quick start evolution loops and advanced development workflows  
- **Task-Based Development**: How reference implementations drive tool improvement

👉 **See [DEVELOP.md](DEVELOP.md)** for complete development documentation, architecture details, and contribution guidelines.

## License

MIT License - see LICENSE file for details. 