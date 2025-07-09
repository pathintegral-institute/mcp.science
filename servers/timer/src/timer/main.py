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

import asyncio
import logging
import os
from typing import Annotated

# The MCP Python SDK is expected to be available at runtime because this server
# is executed via ``uvx ...`` which installs the declared optional
# dependencies for the selected sub-package.  Import errors are intentionally
# *not* swallowed so that problems surface early during startup.
from mcp.server.fastmcp import Context, FastMCP  # type: ignore
from pydantic import Field, NonNegativeInt, PositiveInt

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()),
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
        "A timer tool that waits for a specified duration while providing "
        "progress updates. Useful for simulating delays, testing async operations, "
        "or demonstrating progress reporting. The tool will block for the specified "
        "time and send periodic progress notifications to track completion status. "
        "Returns 'Done' when the wait period is complete."
    ),
)
async def wait(
    time_to_wait: Annotated[NonNegativeInt, Field(description="Total duration to wait in milliseconds (e.g., 5000 for 5 seconds)")],
    ctx: Context,
    notif_interval: Annotated[PositiveInt, Field(description="Optional interval in milliseconds between progress notifications. Defaults to 10000 (10 seconds) if not specified. Use smaller values for more frequent updates.")] = 10000,
) -> str:
    """Block for *time_to_wait* while emitting progress notifications."""

    # Fast-path: if ``time_to_wait`` is zero, finish immediately.
    if time_to_wait == 0:
        return "Done (no wait requested)"

    # Convert to seconds for ``asyncio.sleep``.
    total_seconds: float = time_to_wait / 1000.0
    interval_seconds: float = notif_interval / 1000.0

    elapsed_seconds: float = 0.0
    # If the interval is equal to or larger than the total duration we can
    # skip all intermediate notifications and just sleep once.
    if notif_interval >= time_to_wait:
        await asyncio.sleep(total_seconds)
        logger.debug(f"Sending final progress notification: {time_to_wait}/{time_to_wait} ms")
        await ctx.report_progress(time_to_wait, time_to_wait)
        return "Done"

    # The more common case – emit progress updates periodically.
    while elapsed_seconds + interval_seconds < total_seconds:
        await asyncio.sleep(interval_seconds)
        elapsed_seconds += interval_seconds
        elapsed_ms = int(elapsed_seconds * 1000)
        logger.debug(f"Sending progress notification: {elapsed_ms}/{time_to_wait} ms")
        await ctx.report_progress(elapsed_ms, time_to_wait)

    # Final sleep for any leftover < interval.
    if elapsed_seconds < total_seconds:
        await asyncio.sleep(total_seconds - elapsed_seconds)

    logger.debug(f"Sending final progress notification: {time_to_wait}/{time_to_wait} ms")
    await ctx.report_progress(time_to_wait, time_to_wait)
    return "Done"


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

