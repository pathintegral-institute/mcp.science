from typing import Annotated

from mcp.types import Tool
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    query: Annotated[str, Field(description="The search query from user")]
    max_results: Annotated[int, Field(
        description="The maximum number of results to return",
        ge=1,
        le=20
    )]


search_scholar_tool = Tool(
    name="txyz_search_scholar",
    description="Focused, specialized search for academic and scholarly materials, the results (`ScholarResponse`) are could be papers, articles etc.",
    inputSchema=SearchQuery.model_json_schema()
)

search_web_tool = Tool(
    name="txyz_search_web",
    description="Perform a web search for general purpose information, the results would be resources from web pages.",
    inputSchema=SearchQuery.model_json_schema()
)

search_smart_tool = Tool(
    name="txyz_search_smart",
    description="AI-powered Smart Search handles all the necessary work to deliver the best results. The results may include either scholarly materials or web pages.",
    inputSchema=SearchQuery.model_json_schema()
)
