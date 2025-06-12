"""NEMAD MCP Server"""

import argparse
from . import server


def main():
    """Main CLI entry point for the NEMAD MCP server"""
    parser = argparse.ArgumentParser(description="NEMAD MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport method (default: stdio)",
    )
    
    args = parser.parse_args()
    
    # Run the server
    server.main(args.transport)


__all__ = ["main"]
