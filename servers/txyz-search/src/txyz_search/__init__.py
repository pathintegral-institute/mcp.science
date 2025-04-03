import asyncio

from .server import serve


def main():
    asyncio.run(serve())

if __name__ == "__main__":
    main()
