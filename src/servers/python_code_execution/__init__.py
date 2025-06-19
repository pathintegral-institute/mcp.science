from .server import serve
import asyncio

def main() -> None:
    asyncio.run(serve())

if __name__ == "__main__":
    main()
