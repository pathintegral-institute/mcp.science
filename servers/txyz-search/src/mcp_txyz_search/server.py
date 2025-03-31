
import logging
import os
from typing import Any, Callable, List, Optional, cast

import httpx
from dotenv import load_dotenv
from mcp.server.lowlevel import Server as McpServer
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, ErrorData, TextContent, Tool
from pydantic import BaseModel, ValidationError

from .tools import (SearchQuery, search_scholar_tool, search_smart_tool,
                    search_web_tool)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
load_dotenv()


def _max_result_restriction(max_results: int) -> int:
    return max(1, min(20, max_results))

class TXYZSearchResult(BaseModel):
    title: str
    link: str
    snippet: str
    authors: Optional[List[str]] = None
    number_of_citations: Optional[int] = None

class TXYZSearchResponse(BaseModel):
    results: List[TXYZSearchResult]

class TXYZAPIClient:

    def __init__(self):
        self.api_key = os.getenv("TXYZ_API_KEY", default="")
        self.base_url = os.getenv("TXYZ_API_BASE_URL", default="https://api.txyz.ai/v1")
        self._validate_api_key()

    def _validate_api_key(self):
        if not self.api_key:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message="missing TXYZ_API_KEY from environment variable"
            ))

    async def make_request(self, router: str, data: dict[str, Any]) -> TXYZSearchResponse:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url=f"{self.base_url}/{router}",
                    params=data,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30
                )
                response.raise_for_status()
                return TXYZSearchResponse(**response.json())
            except httpx.HTTPStatusError as e:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"http status error from txyz {router}, see error detail: {str(e)}"
                ))
            except Exception as e:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"failed to retrieve search from txyz {router}, see error detail: {str(e)}"
                ))


def _handle_no_results() -> list[TextContent]:
    """Handle no results case"""
    return [TextContent(type="text", text="No results found")]

def _handle_scholar_result(result: TXYZSearchResult, idx: int) -> TextContent:
    """Handle scholar search result formatting"""
    author_content = f"Authors: {', '.join(result.authors)}" if result.authors else "Authors: Not available"
    citation_content = f"Citations: {result.number_of_citations}" if result.number_of_citations is not None else "Citations: Not available"
    content = f"{idx + 1}. **{result.title}**\n   URL: {result.link}\n   {author_content}\n   {citation_content}\n   Snippet: {result.snippet}\n"
    return TextContent(type="text", text=content)

def _handle_web_result(result: TXYZSearchResult, idx: int) -> TextContent:
    """Handle web search result formatting"""
    content = f"{idx + 1}. **{result.title}**\n   URL: {result.link}\n   Snippet: {result.snippet}\n"
    return TextContent(type="text", text=content)

def _handle_smart_result(result: TXYZSearchResult, idx: int) -> TextContent:
    """Handle smart search result formatting"""
    if result.authors:
        authors_text = f"Authors: {', '.join(result.authors)}"
        citations_text = f"Citations: {result.number_of_citations}" if result.number_of_citations is not None else "Citations: Not available"
        result_text = (
            f"{idx + 1}. **{result.title}** (Scholar)\n"
            f"   URL: {result.link}\n"
            f"   {authors_text}\n"
            f"   {citations_text}\n"
            f"   Snippet: {result.snippet}\n"
        )
    else:
        result_text = (
            f"{idx + 1}. **{result.title}** (Web)\n"
            f"   URL: {result.link}\n"
            f"   Snippet: {result.snippet}\n"
        )
    return TextContent(type="text", text=result_text)


# General Search Function
async def _search(
        router: str,
        query: str,
        max_results: int,
        result_handler: Callable[[TXYZSearchResult, int], TextContent]
    ) -> list[TextContent]:
    """
    General Search Tool

    Args:
        router: API router
        query: search query
        max_results: maximum number of results
        result_handler: function to handle single result

    Returns:
        formatted search results list
    """
    client = TXYZAPIClient()
    response = await client.make_request(
        router=router,
        data={
            "query": query,
            "max_results": _max_result_restriction(max_results)
        }
    )

    if not response.results:
        return _handle_no_results()

    formatted_results = []
    for idx, result in enumerate(response.results):
        formatted_results.append(result_handler(result, idx))
        if idx == max_results - 1:
            break
    return cast(list[TextContent], formatted_results)


async def search_scholar(query: str, max_results: int) -> list[TextContent]:
    return await _search("search/scholar", query, max_results, _handle_scholar_result)


async def search_web(query: str, max_results: int) -> list[TextContent]:
    return await _search("search/web", query, max_results, _handle_web_result)


async def search_smart(query: str, max_results: int) -> list[TextContent]:
    return await _search("search/smart", query, max_results, _handle_smart_result)


async def serve():
    server = McpServer(name="mcp-txyz-search")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [search_scholar_tool, search_web_tool, search_smart_tool]

    @server.call_tool()
    async def call_tool(tool_name: str, arguments: dict[str, Any]) -> list[TextContent]:
        try:
            args = SearchQuery(**arguments)
        except ValidationError as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Invalid arguments for {tool_name}: {str(e)}"
            ))
        match tool_name:
            case search_scholar_tool.name:
                return await search_scholar(args.query, args.max_results)
            case search_web_tool.name:
                return await search_web(args.query, args.max_results)
            case search_smart_tool.name:
                return await search_smart(args.query, args.max_results)
            case _:
                raise McpError(ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Invalid tool name: {tool_name}"
                ))


    async with stdio_server() as (read_stream, write_stream):
        logger.info("Starting TXYZ Search Server...")
        await server.run(
            read_stream,
            write_stream,
            initialization_options=server.create_initialization_options(),
            raise_exceptions=False
        )
