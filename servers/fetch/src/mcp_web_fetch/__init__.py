import argparse
import asyncio

from .fetch import serve

DEFAULT_USER_AGENT = "ModelContextProtocol/1.0 (User-Specified; +https://github.com/modelcontextprotocol/servers)"

def main():
    parser = argparse.ArgumentParser("a general web content fetch tool")

    parser.add_argument(
        "--user-agent",
        type=str,
        default=DEFAULT_USER_AGENT,
        help="User-Agent header to use for requests"
    )
    args = parser.parse_args()

    asyncio.run(serve(args.user_agent))


if __name__ == "__main__":
    main()
