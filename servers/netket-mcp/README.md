# Self-Evolving MCP Tools for Scientific Computing

A framework for developing and iteratively improving Model Context Protocol (MCP) tools for scientific Python libraries through automated feedback loops.

## Overview

This repository demonstrates a novel approach to building MCP tools that can self-evolve and improve through iterative testing against scientific computing tasks. Rather than manually crafting perfect tools from the start, this framework allows tools to grow and adapt based on real-world usage patterns and feedback.

## Framework Architecture

The framework consists of four core components that work together in a continuous improvement loop:

### 1. Memory Manager (`netket_jsons.py`)
A persistent state manager that tracks scientific projects and workflows, serving as a "scratch paper" for complex multi-step analyses. It maintains:
- System configurations and parameters
- Intermediate results and computations  
- Analysis history and metadata
- File organization and storage

### 2. Language Parser (`netket_schemas.py`)
Natural language processing schemas that convert human descriptions into structured scientific objects:
- Lattice geometries ("4x4 square lattice" → NetKet graph objects)
- Physical systems ("10 fermions with spin-1/2" → Hilbert spaces)
- Model specifications ("SSH model with t1=1, t2=0.2" → Hamiltonian operators)

### 3. MCP Server (`mcp_server.py`)
The main tool server providing scientific computing capabilities:
- Quantum system creation and management
- Energy spectrum calculations
- Parameter sweeps and phase transitions
- Data visualization and analysis
- Results storage and retrieval

### 4. Task Set (`task-set/`)
Static reference implementations of common scientific computing tasks that serve as:
- **Benchmarks**: Ground truth for validating tool outputs (never modified)
- **Instructions**: Clear examples showing what the tools should accomplish
- **Test cases**: Comprehensive coverage of scientific workflows to be replicated

## Self-Evolution Loop

```
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│ Task Set  │───▶│ AI Agent  │───▶│   Tool    │───▶│ Compare & │───▶│  Update   │
│ (Static)  │    │ Use Tools │    │ Results   │    │ Feedback  │    │   Tools   │
└───────────┘    └───────────┘    └───────────┘    └───────────┘    └───────────┘
     │                                   │              ▲                 │
     │                                   │              │                 │
     ▼                                   ▼              │                 │
┌───────────┐    ┌───────────┐         ┌─┴──────────────┴─┐               │
│  Python   │───▶│Reference  │────────▶│     Match?       │               │
│ Scripts   │    │ Results   │         │   ✓ Done         │               │
└───────────┘    └───────────┘         │   ✗ Iterate  ────┼───────────────┘
                                       └──────────────────┘
```

The evolution process:
1. **Apply Tools**: AI agent uses MCP tools to replicate task workflows from the static task set
2. **Generate Ground Truth**: Directly execute the Python scripts to get reference results
3. **Compare**: Tool results vs direct Python execution results (plots, data, analysis)
4. **Analyze Gaps**: Identify differences, errors, and missing capabilities in the tools
5. **Update Tools**: Modify MCP tools (schemas, server functions, logic) to close gaps
6. **Iterate**: Repeat until MCP tools can perfectly replicate Python script results

## Key Principles

- **Generalizability**: Build minimal, reusable building blocks rather than task-specific solutions
- **Iterative Improvement**: Tools evolve through usage, not upfront design
- **Scientific Accuracy**: Maintain correctness while improving usability
- **Natural Language Interface**: Enable intuitive interaction with complex scientific concepts

## Getting Started

### Prerequisites
- [Cursor](https://cursor.com/) IDE with MCP support
- Python 3.10+
- Required scientific libraries (see `requirements.txt`)

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd MCP_NetKet
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Cursor MCP**:
   Update the path in `.cursor/mcp.json` to your local directory:
   ```json
   {
     "mcpServers": {
       "netket": {
         "command": "uv",
         "args": [
           "run",
           "--with", "mcp[cli]",
           "--with", "matplotlib",
           "--with", "scipy", 
           "--with", "netket",
           "--with", "numpy",
           "mcp",
           "run",
           "/path/to/your/local/MCP_NetKet/mcp_server.py"
         ]
       }
     }
   }
   ```

4. **Start using the tools**:
   - Open Cursor
   - Enable agent mode
   - Start with: "Please use the MCP tools to implement the SSH analysis task"

## Usage Example

The framework enables natural language interactions with complex scientific computations:

```
Human: "Analyze the SSH model edge states for a 24-site chain with t1=1.0, t2=0.2"

AI Agent: 
1. Creates quantum system
2. Sets up 24-site chain lattice  
3. Configures 1 spinless fermion
4. Builds SSH Hamiltonian
5. Computes full energy spectrum
6. Analyzes zero-energy edge states
7. Generates visualization plots
```

## Contributing

### Quick Start: Your First Evolution Loop

Get started contributing in 5 minutes:

1. **Setup Environment**:
   ```bash
   git clone <repo-url> && cd MCP_NetKet
   pip install -r requirements.txt
   # Update .cursor/mcp.json with your local path
   ```

2. **Run Reference Task**:
   ```bash
   python task-set/analyze_ssh.py
   # ✓ Generates ground truth results in /tmp/quantum_systems/
   ```

3. **Try with MCP Tools** - Open Cursor, enable agent mode, and prompt:
   ```
   "Use the MCP tools to analyze the SSH model for a 24-site chain with t1=1.0, t2=0.2, 
   comparing your results to task-set/analyze_ssh.py"
   ```

4. **Compare Results**:
   - **Reference**: Check `/tmp/quantum_systems/system_*/ssh_full_spectrum.png`
   - **Your Tools**: Did you get the same energy spectrum and edge state localization?
   - **Gaps Found**: Missing features? Wrong values? Poor visualizations?

5. **Evolve**: Update the MCP tools based on what you learned, then repeat until perfect match!

**Expected First Run**: Tools will likely miss some capabilities. That's the point - now you know exactly what to improve.

### Advanced Contributing

To improve the MCP tools further:

1. **Add new tasks**: Create reference implementations in `task-set/`
2. **Run evolution loop**: Use Cursor agent mode with the prompt:
   > "Please use the tools to implement each task in the task set, using the python code as instruction and benchmark. Try to develop general tools to optimize the mcp_server and seed tools so that all tasks can be conquered. Don't build task-specific tools, always find general solutions. Iterate until the tools can perfectly solve all tasks."

3. **Test generalization**: Ensure new capabilities work across multiple scientific domains
4. **Document improvements**: Update schemas and tool descriptions

## Current Capabilities

- **Quantum Many-Body Physics**: SSH model, Hubbard model, Heisenberg chains
- **Lattice Systems**: 1D chains, 2D square/triangular lattices, 3D cubic lattices  
- **Analysis Tools**: Energy spectra, phase transitions, parameter sweeps
- **Visualization**: Automatic plot generation and result display
- **State Management**: Persistent storage of complex scientific workflows

## Future Directions

This framework can be extended to other scientific domains:
- **Molecular Dynamics**: Protein folding, drug discovery
- **Materials Science**: Electronic structure, phonon calculations  
- **Astrophysics**: N-body simulations, cosmological models
- **Bioinformatics**: Sequence analysis, structural biology

The self-evolution approach ensures tools adapt to the specific needs and workflows of each scientific field while maintaining general applicability.

## License

MIT License - see LICENSE file for details. 