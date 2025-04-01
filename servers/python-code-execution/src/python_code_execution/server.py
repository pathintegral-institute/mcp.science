
import logging
import os
from typing import Any, Callable, List, Optional, cast
from multiprocessing import Process, Queue
import re
import subprocess
from mcp.server.lowlevel import Server as McpServer
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, ErrorData, TextContent, Tool
from pydantic import BaseModel, ValidationError
from .local_python_executor import evaluate_python_code
logger = logging.getLogger(__name__)
class PythonCodeExecutionArgs(BaseModel):
    code: str


def execute_code_in_process(code: str, result_queue: Queue):
    """Execute the code in a separate process and put the result in the queue"""
    try:
        result = evaluate_python_code(code)
        result_queue.put(("success", result))
    except Exception as e:
        result_queue.put(("error", str(e)))

async def python_code_execution_tool(code: str) -> TextContent:
    """Execute the generated python code in a sandboxed environment."""
    # Clean the code by removing markdown code blocks if present
    cleaned_code = re.sub(r'```(?:python|py)?\s*\n|```\s*$', '', code)
    
    # Create a queue for getting the result
    result_queue = Queue()
    
    # Create and start the process
    process = Process(
        target=execute_code_in_process,
        args=(cleaned_code, result_queue)
    )
    process.start()
    
    try:
        # Wait for the process to complete or timeout
        process.join(timeout=15)
        
        if process.is_alive():
            # If process is still running after timeout, terminate it
            process.terminate()
            process.join()
            result = "Execution timed out. The code took too long to run."
        else:
            # Get the result from the queue
            if not result_queue.empty():
                status, output = result_queue.get()
                if status == "success":
                    result = output
                else:
                    result = f"Error: {output}"
            else:
                result = "No output received from the execution"
                
    except Exception as e:
        result = f"An error occurred while executing the code: {str(e)}"
    finally:
        # Ensure the process is terminated if still running
        if process.is_alive():
            process.terminate()
            process.join()

    return TextContent(
        text=result,
        type="text",
    )


python_code_execution_tool = Tool(
    name="python_code_execution",
    description=python_code_execution.__doc__,
    inputSchema=PythonCodeExecutionArgs.model_json_schema()
)

async def serve():
    server = McpServer(name="mcp-python_code_execution")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [python_code_execution_tool]

    @server.call_tool()
    async def call_tool(tool_name: str, arguments: dict[str, Any]) -> list[TextContent]:
        try:
            args = PythonCodeExecutionArgs(**arguments)
        except ValidationError as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Invalid arguments for {tool_name}: {str(e)}"
            ))
        match tool_name:
            case python_code_execution_tool.name:
                return await python_code_execution(args.code)
            case _:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Invalid tool name: {tool_name}"
                ))


    async with stdio_server() as (read_stream, write_stream):
        logger.info("Starting LocalPython Code Execution Server...")
        await server.run(
            read_stream,
            write_stream,
            initialization_options=server.create_initialization_options(),
            raise_exceptions=False
        )
