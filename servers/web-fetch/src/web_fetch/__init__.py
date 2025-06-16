import click
from typing import Literal
from web_fetch.fetch import mcp


@click.command()
@click.option(
    "-t",
    "--transport",
    type=click.Choice(["stdio", "sse", "streamable-http"]),
    default="stdio",
    help="Transport to use for requests",
)
def main(transport: Literal["stdio", "sse", "streamable-http"]):
    import logging

    logger = logging.getLogger(__name__)

    logger.info(
        f"Starting server with transport: {transport}"
    )
    mcp.run(transport)


if __name__ == "__main__":
    main()
