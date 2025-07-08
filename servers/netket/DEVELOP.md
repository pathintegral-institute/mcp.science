# NetKet MCP Server - Development Guide

This document describes the self-evolving framework architecture and development principles behind the NetKet MCP server.

## Overview

This server demonstrates a novel approach to building MCP tools that can self-evolve and improve through iterative testing against scientific computing tasks. Rather than manually crafting perfect tools from the start, this framework allows tools to grow and adapt based on real-world usage patterns and feedback.

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

## Development Setup

### Prerequisites
- Python 3.10+
- Git for version control
- [Cursor](https://cursor.com/) IDE with MCP support (recommended)

### Local Development

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mcp.science/servers/netket
   ```

2. **Install and run**:
   ```bash
   pip install -e .
   mcp-science-netket
   ```

4. **Configure Cursor MCP for local development**:
   Update `.cursor/mcp.json` to point to your local development server:
   ```json
   {
    "mcpServers": {
        "netket": {
            "command": "uv",
            "args": [
                "run",
                "--with",
                "mcp[cli]",
                "--with",
                "matplotlib",
                "--with",
                "scipy",
                "--with",
                "netket",
                "--with",
                "numpy",
                "mcp",
                "run",
                "servers/netket/src/netket/mcp_server.py"
            ]
        }
    }
   ```

## Contributing

### Quick Start: Your First Evolution Loop

Get started contributing in 5 minutes:

1. **Setup Environment**:
   ```bash
   git clone <repo-url> && cd servers/netket
   pip install -e .
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

### Code Structure

```
src/netket/
├── mcp_server.py      # Main MCP server with tool definitions
├── netket_schemas.py  # Pydantic schemas for natural language parsing
├── netket_jsons.py    # JSON state management and persistence
└── __init__.py        # Package entry point

task-set/              # Reference implementations (never modify)
├── analyze_ssh.py     # SSH model analysis benchmark
├── analyze_ising.py   # Ising model analysis benchmark
└── ...

tests/                 # Unit tests and integration tests
```

### Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run specific task benchmarks:
```bash
python task-set/analyze_ssh.py
python task-set/analyze_ising.py
```

## Related Work

Our self-evolving MCP framework shares conceptual similarities with other projects exploring AI agent improvement and iterative development:

- **[Roo Code](https://github.com/RooCodeInc/Roo-Code)**: Provides "a whole dev team of AI agents in your code editor" that can autonomously work on development tasks. Like our framework, it focuses on agents that can evolve and improve their capabilities through usage.

- **[mint-bench](https://xwang.dev/mint-bench/)**: A benchmarking framework for evaluating and improving AI tools through systematic testing against reference tasks, similar to our task-set approach for driving tool evolution.

These projects demonstrate the broader trend toward self-improving AI systems that learn from real-world usage patterns rather than static training.

## Future Directions

This framework can be extended to other scientific domains:
- **Molecular Dynamics**: Protein folding, drug discovery
- **Materials Science**: Electronic structure, phonon calculations  
- **Astrophysics**: N-body simulations, cosmological models
- **Bioinformatics**: Sequence analysis, structural biology

The self-evolution approach ensures tools adapt to the specific needs and workflows of each scientific field while maintaining general applicability.

## Architecture Decisions

### Why Self-Evolution?
Traditional MCP servers require extensive upfront design and manual optimization. Our approach:
- **Reduces development time**: Let AI agents discover what tools they actually need
- **Improves accuracy**: Real usage patterns guide tool development
- **Enables generalization**: Common patterns emerge across different scientific domains
- **Maintains quality**: Reference implementations ensure correctness

### Why Natural Language Schemas?
Scientific users think in domain-specific language, not code:
- **"4x4 square lattice"** is more intuitive than `Graph(nodes=16, edges=[(0,1), (1,2), ...])`
- **"SSH model with t1=1, t2=0.2"** is clearer than manual Hamiltonian construction
- **Natural language bridges** the gap between human intuition and precise computation

### Why Task Sets?
Static reference implementations provide:
- **Objective benchmarks**: Clear targets for tool development
- **Comprehensive coverage**: Ensure tools handle diverse scientific workflows  
- **Quality assurance**: Never-changing ground truth prevents regression
- **Learning examples**: Show AI agents what the tools should accomplish

## Contributing Guidelines

1. **Never modify task-set files** - they are permanent benchmarks
2. **Focus on generalization** - avoid task-specific solutions
3. **Test thoroughly** - ensure new features work across multiple domains
4. **Document clearly** - update schemas and tool descriptions
5. **Measure improvement** - compare against reference implementations

## License

MIT License - see LICENSE file for details. 