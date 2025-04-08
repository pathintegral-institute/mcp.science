# Python Code Execution Server

A secure sandboxed Python code execution environment for MCP (Model-Client-Program) architecture.

Adapted from <https://huggingface.co/docs/smolagents/en/index> with added security and image support

## Features

- Safe execution of Python code with restricted imports and resource limits
- Support for matplotlib visualization
- Configurable resource limits (memory, CPU time)
- Error handling and formatted output
- Protection against dangerous operations and imports
- None Docker Solution

### Execute Python code

This server provides a tool called `python_code_execution` that can be used by LLM agents to execute Python code securely.

## Allowed Imports

- Standard library: `collections`, `datetime`, `itertools`, `math`, `queue`, `random`, `re`, `stat`, `statistics`, `time`, `unicodedata`
- Scientific libraries: `numpy`, `matplotlib`

## MCP parameter

```json
    "mcp-python-code-execution": {
        "command": "uvx",
        "args": [
            "--from",
            "git+https://github.com/pathintegral-institute/mcp.science@main#subdirectory=servers/python-code-execution",
            "mcp-python-code-execution"
        ],
        "env": {}
    }
```

## Warning

Due to bugs in `resource` package in Mac os, we only support it in linux environments
