from loguru import logger
from .server import mcp


def main():
    """Entry point for the Materials Project MCP server"""
    logger.info("starting materials project server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
