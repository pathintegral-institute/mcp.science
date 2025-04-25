from .server import mcp
from loguru import logger


def main() -> None:
    logger.info("starting gpaw computation server...")
    mcp.run(transport="stdio")
