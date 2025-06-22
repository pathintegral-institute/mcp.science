"""Timer MCP server.

This server exposes a single tool – ``wait`` – that blocks for a specified
amount of time while periodically **streaming progress updates** back to the
client.  Both the total wait time and the progress-notification interval are
expressed in *milliseconds* so that the tool can be used conveniently from
LLMs, which generally handle integers better than ``datetime`` objects.

The implementation purposefully depends only on the public MCP Python API
(``mcp.server.FastMCP`` and ``mcp.types.TextContent``) so that it remains
light-weight and free of any additional runtime requirements.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Annotated, AsyncGenerator, List

# The MCP Python SDK is expected to be available at runtime because this server
# is executed via ``uvx ...`` which installs the declared optional
# dependencies for the selected sub-package.  Import errors are intentionally
# *not* swallowed so that problems surface early during startup.
from mcp.server import FastMCP  # type: ignore
from mcp.types import TextContent  # type: ignore
from pydantic import Field, NonNegativeInt, PositiveInt

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# MCP setup
# -----------------------------------------------------------------------------

mcp = FastMCP("mcp-timer")


# -----------------------------------------------------------------------------
# Tool implementation
# -----------------------------------------------------------------------------


@mcp.tool(
    name="wait",
    description=(
        "Wait for `time_to_wait` milliseconds, sending progress-update "
        "notifications every `notif_interval` milliseconds before returning "
        "`Done`.  If `notif_interval` is greater than `time_to_wait` then the "
        "tool will send **no** intermediate progress updates."
    ),
)
async def wait(
    time_to_wait: Annotated[NonNegativeInt, Field(description="Total time to wait, **in milliseconds**")],
    notif_interval: Annotated[PositiveInt, Field(description="Interval between progress updates, **in milliseconds**")],
) -> List[TextContent] | AsyncGenerator[TextContent, None]:
    """Block for *time_to_wait* while emitting progress notifications.

    The function chooses between a normal return value and an asynchronous
    generator based on the provided parameters.  Using an *async generator*
    allows the MCP framework to stream intermediate messages back to the
    client without holding up the entire response until the very end.
    """

    # Fast-path: if ``time_to_wait`` is zero, finish immediately.
    if time_to_wait == 0:
        return [TextContent(type="text", text="Done (no wait requested)")]

    # Convert to seconds for ``asyncio.sleep``.
    total_seconds: float = time_to_wait / 1000.0
    interval_seconds: float = notif_interval / 1000.0

    # Asynchronous *generator* that yields progress updates.
    async def _ticker() -> AsyncGenerator[TextContent, None]:
        elapsed: float = 0.0
        # If the interval is equal to or larger than the total duration we can
        # skip all intermediate notifications and just sleep once.
        if notif_interval >= time_to_wait:
            await asyncio.sleep(total_seconds)
            yield TextContent(type="text", text="Done")
            return

        # The more common case – emit progress updates periodically.
        while elapsed + interval_seconds < total_seconds:
            await asyncio.sleep(interval_seconds)
            elapsed += interval_seconds
            percent = int(round((elapsed / total_seconds) * 100))
            remaining_ms = max(0, int((total_seconds - elapsed) * 1000))
            yield TextContent(
                type="text",
                text=f"Progress: {percent}% (≈{remaining_ms} ms remaining)",
            )

        # Final sleep for any leftover < interval.
        if elapsed < total_seconds:
            await asyncio.sleep(total_seconds - elapsed)

        yield TextContent(type="text", text="Done")

    return _ticker()


# -----------------------------------------------------------------------------
# Entry-point
# -----------------------------------------------------------------------------


def main() -> None:  # noqa: D401 – simple relay function
    """Start the timer MCP server."""

    logger.info("Starting timer MCP server …")
    # The server will read/write JSON-RPC messages through **STDIO** so that it
    # can be managed easily by any MCP-compatible client.
    mcp.run("stdio")


if __name__ == "__main__":
    main()

