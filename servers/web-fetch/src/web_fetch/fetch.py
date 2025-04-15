import json
import os
from enum import StrEnum
from typing import Annotated

import httpx
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, ErrorData, TextContent
from pydantic import AnyUrl, Field
from mcp.server import FastMCP

from .utils import (
    convert_html_to_markdown,
    convert_pdf_to_plain_text,
    extract_media_type,
)

DEFAULT_USER_AGENT = "ModelContextProtocol/1.0 (User-Specified; +https://github.com/modelcontextprotocol/servers)"


class ResponseMediaType(StrEnum):
    HTML = "text/html"
    PDF = "application/pdf"
    JSON = "application/json"


async def async_fetch(
    url: str, user_agent: str, timeout: float = 30.0, follow_redirects: bool = True
) -> httpx.Response:
    """
    fetch web content

    Args:
        url: target url
        timeout: timeout in seconds
        follow_redirects: whether to follow redirects
    Returns:
        httpx.Response: HTTP response object

    Raises:
        McpError: when request fails, contains detailed error information
    """
    default_headers = {"User-Agent": user_agent}

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(timeout), follow_redirects=follow_redirects
        ) as client:
            response = await client.get(url, headers=default_headers)
            response.raise_for_status()
            return response

    except httpx.HTTPStatusError as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"HTTP Status Code Error {e.response.status_code}: {e.response.text}",
            )
        )

    except httpx.TimeoutException:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR, message=f"HTTP Timeout Error for {timeout} seconds"
            )
        )

    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Unexpected Error During HTTP Request: {str(e)}",
            )
        )


async def fetch(
    url: str, user_agent: str, force_raw: bool = False
) -> list[TextContent]:
    """Fetch URL and return content according to its content type."""
    response: httpx.Response = await async_fetch(url, user_agent=user_agent)
    if force_raw:
        return [TextContent(text=response.text, type="text")]

    media_type = extract_media_type(response.headers["Content-Type"])

    match media_type:
        case ResponseMediaType.HTML:
            return [
                TextContent(text=convert_html_to_markdown(response.text), type="text")
            ]
        case ResponseMediaType.JSON:
            return [TextContent(text=json.dumps(response.json()), type="text")]
        case ResponseMediaType.PDF:
            return [
                TextContent(
                    text=convert_pdf_to_plain_text(response.content), type="text"
                )
            ]
        case _:
            # return raw content
            return [TextContent(text=response.text, type="text")]


mcp = FastMCP("mcp-web-fetch")


@mcp.tool(
    name="fetch-web",
    description="Fetch URL and return content according to its content type.",
)
async def fetch_web(
    url: Annotated[AnyUrl, Field(description="URL to fetch")],
    raw: Annotated[bool, Field(description="Return raw content", default=False)],
):
    return await fetch(str(url), os.getenv("USER_AGENT", DEFAULT_USER_AGENT), raw)
