from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent
import logging

# Set up logging (this just prints messages to your terminal for debugging)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the MCP server object
mcp = FastMCP()

# Here’s where you define your tools (functions the AI can use)
@mcp.tool()
def add(a: int, b: int) -> TextContent:
    """Add two numbers.

    Args:
        a: the first integer to be added
        b: the second integer to be added
    
    Return:
        The sum of the two integers, as a string."""
    return TextContent(type="text", text=str(a + b))

# The return format should be one of the types defined in mcp.types. The commonly used ones include TextContent, ImageContent, BlobResourceContents.
# In the case of a string, you can also directly use `return str(a + b)` which is equivalent to `return TextContent(type="text", text=str(a + b))`

@mcp.tool()
def get_image_of_flower():
    """Get an image of flower

    Return:
        Image of flower in png."""
    image_base64 = "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"
    # if you're not familiar with base64, you can see https://en.wikipedia.org/wiki/Base64

    return ImageContent(data=image_base64, mimeType="image/png", type="image")


# This is the main entry point for your server
def main():
    logger.info('Starting your-new-server')
    mcp.run('stdio')

if __name__ == "__main__":
    main()