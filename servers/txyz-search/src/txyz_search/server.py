import logging
import os
from typing import Any, Callable, List, Optional, cast, Annotated

import httpx
from dotenv import load_dotenv
from mcp.server import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, ErrorData, TextContent
from pydantic import BaseModel


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
load_dotenv()

mcp = FastMCP("txyz_search")


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
        self.base_url = os.getenv(
            "TXYZ_API_BASE_URL", default="https://api.txyz.ai/v1")
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
    as_ylo: Optional[int],
    as_yhi: Optional[int],
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
    payload = {
        "query": query,
        "max_results": _max_result_restriction(max_results)
    }
    if as_ylo:
        payload["as_ylo"] = as_ylo
    if as_yhi:
        payload["as_yhi"] = as_yhi

    response = await client.make_request(
        router=router,
        data=payload)

    if not response.results:
        return _handle_no_results()

    formatted_results = []
    for idx, result in enumerate(response.results):
        formatted_results.append(result_handler(result, idx))
        if idx == max_results - 1:
            break
    return cast(list[TextContent], formatted_results)


@mcp.tool(
    name="txyz_search_scholar",
    description="Focused, specialized search for academic and scholarly materials, the results (`ScholarResponse`) are could be papers, articles etc.",
)
async def search_scholar(query: str,
                         max_results: int,
                         as_ylo: Annotated[Optional[int],
                                           "year of publication lower bound"] = None,
                         as_yhi: Annotated[Optional[int], "year of publication upper bound"] = None) -> list[TextContent]:
    """
    query: str
    max_results: int
    as_yhi: Optional[int], year of publication upper bound
    as_ylo: Optional[int], year of publication lower bound
    """
    return await _search("search/scholar", query, max_results, as_ylo, as_yhi, _handle_scholar_result)


@mcp.tool(
    name="txyz_search_web",
    description="Perform a web search for general purpose information, the results would be resources from web pages.",
)
async def search_web(query: str,
                     max_results: int,
                     as_ylo: Annotated[Optional[int],
                                       "year of publication lower bound"] = None,
                     as_yhi: Annotated[Optional[int], "year of publication upper bound"] = None) -> list[TextContent]:
    return await _search("search/web", query, max_results, as_ylo, as_yhi, _handle_web_result)


@mcp.tool(
    name="txyz_search_smart",
    description="AI-powered Smart Search handles all the necessary work to deliver the best results. The results may include either scholarly materials or web pages.",
)
async def search_smart(query: str,
                       max_results: int,
                       as_ylo: Annotated[Optional[int],
                                         "year of publication lower bound"] = None,
                       as_yhi: Annotated[Optional[int], "year of publication upper bound"] = None) -> list[TextContent]:
    return await _search("search/smart", query, max_results, as_ylo, as_yhi, _handle_smart_result)
