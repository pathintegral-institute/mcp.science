from .server import mcp
from .utils import DEFAULT_EXECUTION_WAIT_TIMEOUT
import argparse
import os
import logging

def main():
    parser = argparse.ArgumentParser(description="Jupyter MCP Server for Code Execution")
    parser.add_argument("--wait-execution-timeout", type=int, default=DEFAULT_EXECUTION_WAIT_TIMEOUT, help="Wait execution timeout in seconds")
    args = parser.parse_args()

    os.environ["WAIT_EXECUTION_TIMEOUT"] = str(args.wait_execution_timeout)

    logger = logging.getLogger(__name__)
    logger.info("Starting Jupyter MCP Server")

    mcp.run(transport="stdio")
