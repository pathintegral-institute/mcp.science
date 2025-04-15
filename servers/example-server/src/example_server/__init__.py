from mcp.server.fastmcp import FastMCP
import base64
import logging
from mcp.types import TextContent, ImageContent
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP()


@mcp.tool()
async def add(a: int, b: int) -> str:
    """Add two numbers together.

    This tool takes two numbers as input and returns the result of adding them together.
    """
    logger.info('Adding numbers')
    return str(a + b)


@mcp.tool()
async def reverse(text: str) -> str:
    """Reverse the input text."""
    logger.info('Reversing text')
    return text[::-1]


@mcp.tool(name="get_photo_of_flowers", description="Get a photo of jasmine flowers.")
async def get_photo_of_flowers() -> list[TextContent | ImageContent]:
    """Get image of flowers."""
    logger.info('Getting image of flowers')
    script_dir = Path(__file__).parent
    image_path = script_dir / "assets" / "jasmine.jpg"
    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode("utf-8")
    return [
        TextContent(text="this is a photo of flowers", type="text"),
        ImageContent(data=img_base64,
                     type="image", mimeType="image/png"),
    ]


def main():
    # Start server
    logger.info('Starting example-server')
    mcp.run('stdio')
