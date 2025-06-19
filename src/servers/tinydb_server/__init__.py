from .main import server_main


def main():
    """Entry point for the tinydb-server."""
    server_main()


__all__ = ["server_main", "main"]
