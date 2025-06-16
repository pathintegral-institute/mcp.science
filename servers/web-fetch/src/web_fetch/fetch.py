import os
from typing import Annotated, List

import httpx
from mcp.types import TextContent, ImageContent
from pydantic import AnyUrl, Field
from mcp.server import FastMCP
import requests
import base64


async def fetch(url: str, jina_api_key: str) -> List[TextContent]:
    """Fetch a URL and return the content.

    Args:
        url: The URL to fetch
        jina_api_key: Jina API key

    Returns:
        TextContent containing canvas information
    """
    llm_results = []

    def crawl(url: str) -> str:
        headers = {"Content-Type": "application/json", "X-Return-Format": "markdown", "X-With-Images-Summary": "true"}
        if jina_api_key:
            headers["Authorization"] = f"Bearer {jina_api_key}"

        data = {"url": url}
        response = requests.post("https://r.jina.ai/", headers=headers, json=data)
        return response.text

    try:
        content = crawl(url)
        llm_results.append(TextContent(type="text", text=content))
    except Exception as e:
        llm_results.append(TextContent(type="text", text=f"Failed to fetch URL {url!r}: {e}"))

    return llm_results


mcp = FastMCP("mcp-web-fetch")


@mcp.tool(
    name="fetch-web",
    description="Fetch a URL and return the content. Images will be returned in ![]() format. DO NOT FETCH image_urls, for images use read-image-url instead.",
)
async def fetch_web(
    url: Annotated[AnyUrl, Field(description="URL to fetch")]
):
    return await fetch(str(url), os.getenv("JINA_API_KEY", ""))


@mcp.tool(
    name="read-image-url",
    description="Read images from URLs, convert to LLM readable format.",
)
def read_image_url(image_urls: List[str]) -> List[ImageContent| TextContent]:
    """Read images from URLs, convert to base64, and return the image content.

    Args:
        image_urls: List of URLs of the images to read

    Returns:
        ImageContent containing the base64 encoded image data
    """
    llm_results: list[ImageContent | TextContent] = []
    message_results: list[TextContent] = []

    for image_url in image_urls:
        # Convert to base64
        try:
            image_content = httpx.get(image_url).content
        except Exception as e:
            llm_results.append(TextContent(type="text", text=f"Failed to read image {image_url!r}: {e}"))
            message_results.append(TextContent(type="text", text=f"Failed to read image {image_url!r}: {e}"))
            continue
        mime_type = "image/jpeg"
        if image_content.startswith(b"\xff\xd8\xff"):
            mime_type = "image/jpeg"
        elif image_content.startswith(b"\x89PNG\r\n\x1a\n"):
            mime_type = "image/png"
        elif image_content.startswith(b"RIFF") and b"WEBP" in image_content[:12]:
            mime_type = "image/webp"
        else:
            llm_results.append(
                TextContent(
                    type="text",
                    text=f"Unsupported image type {mime_type!r} for {image_url!r}: only jpeg, png, webp are supported",
                )
            )
            message_results.append(
                TextContent(
                    type="text",
                    text=f"Unsupported image type {mime_type!r} for {image_url!r}: , only jpeg, png, webp are supported",
                )
            )
            continue
        image_data = base64.standard_b64encode(image_content).decode("utf-8")
        llm_results.append(ImageContent(type="image", data=image_data, mimeType=mime_type))

    return llm_results