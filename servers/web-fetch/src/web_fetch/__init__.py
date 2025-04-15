import click
import os
from web_fetch.fetch import mcp, DEFAULT_USER_AGENT


@click.command()
@click.option(
    "-t",
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport to use for requests",
)
@click.option(
    "-u",
    "--user-agent",
    type=str,
    default=DEFAULT_USER_AGENT,
    help="User-Agent header to use for requests",
)
def main(transport: str, user_agent: str):
    import logging

    logger = logging.getLogger(__name__)

    logger.info(
        f"Starting server with transport: {transport} and user agent: {user_agent!r}"
    )
    os.environ["USER_AGENT"] = user_agent
    mcp.run(transport)


if __name__ == "__main__":
    main()
