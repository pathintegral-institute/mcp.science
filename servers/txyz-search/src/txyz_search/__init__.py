import click
from .server import mcp


@click.command()
@click.option(
    "-t",
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport to use for requests",
)
def main(transport: str):
    import logging

    logger = logging.getLogger(__name__)

    logger.info(
        f"Starting server with transport: {transport}"
    )
    mcp.run(transport)


if __name__ == "__main__":
    main()