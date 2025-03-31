import json
from enum import StrEnum
from typing import Annotated, Any, Dict

import httpx
from mcp.server.lowlevel import Server as McpServer
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, ErrorData, TextContent, Tool
from pydantic import AnyUrl, BaseModel, Field, ValidationError

from .utils import (
    convert_html_to_markdown,
    convert_pdf_to_plain_text,
    extract_media_type,
)


class ResponseMediaType(StrEnum):
    HTML = "text/html"
    PDF = "application/pdf"
    JSON = "application/json"


async def async_fetch(
    url: str,
    user_agent: str,
    timeout: float = 30.0,
    follow_redirects: bool = True
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
    default_headers = {
        'User-Agent': user_agent
    }

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=follow_redirects
        ) as client:
            response = await client.get(url, headers=default_headers)
            response.raise_for_status()
            return response

    except httpx.HTTPStatusError as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"HTTP Status Code Error {e.response.status_code}: {e.response.text}"
            )
        )

    except httpx.TimeoutException:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"HTTP Timeout Error for {timeout} seconds"
            )
        )

    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Unexpected Error During HTTP Request: {str(e)}"
            )
        )


async def fetch(url: str, user_agent: str, force_raw: bool = False) -> list[TextContent]:
    """ Fetch URL and return content according to its content type.
    """
    response: httpx.Response = await async_fetch(url, user_agent=user_agent)
    if force_raw:
        return [TextContent(text=response.text, type="text")]

    media_type = extract_media_type(response.headers["Content-Type"])

    match media_type:
        case ResponseMediaType.HTML:
            return [TextContent(text=convert_html_to_markdown(response.text), type="text")]
        case ResponseMediaType.JSON:
            return [TextContent(text=json.dumps(response.json()), type="text")]
        case ResponseMediaType.PDF:
            return [TextContent(text=convert_pdf_to_plain_text(response.content), type="text")]
        case _:
            # return raw content
            return [TextContent(text=response.text, type="text")]


class FetchArgs(BaseModel):
    url: Annotated[AnyUrl, Field(description="URL to fetch")]
    raw: bool = Field(description="Return raw content", default=False)


async def serve(user_agent: str):

    server = McpServer("mcp-web-fetch")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="fetch-web",
                description="Fetch URL and return content according to its content type.",
                inputSchema=FetchArgs.model_json_schema()
            )
        ]


    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]):
        if not name == "fetch-web":
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Unknown tool name: {name}"
                )
            )

        try:
            args = FetchArgs(**arguments)
            return await fetch(str(args.url), user_agent, args.raw)
        except ValidationError as e:
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Invalid arguments: {str(e)}"
                )
            )
        except McpError as e:
            raise e
        except Exception as e:
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Unexpected fetching error: {str(e)}"
                )
            )


    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream=read_stream,
            write_stream=write_stream,
            initialization_options=server.create_initialization_options(),
            raise_exceptions=True
        )
