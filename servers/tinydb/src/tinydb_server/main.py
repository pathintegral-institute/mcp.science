from mcp.server.fastmcp import FastMCP
import logging
import os
import argparse
import sys
import json
from tinydb import TinyDB, Query, where

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger("tinydb-server")

# Global db instance
db = None
# This will hold the db file path received from argparse or set by tests
_db_file_path_for_get_db = None


def get_db(db_file_path_from_arg=None):
    """
    Gets the TinyDB instance. Initializes or re-initializes if the target db_file_path changes
    or if it's not initialized.
    The path for the DB is determined by:
    1. db_file_path_from_arg (if provided, typically from CLI or direct test call)
    2. _db_file_path_for_get_db (global, set by main() from CLI or by tests)
    """
    global db
    global _db_file_path_for_get_db

    target_db_path = db_file_path_from_arg if db_file_path_from_arg else _db_file_path_for_get_db

    if not target_db_path:
        # This case should ideally not be hit if main() correctly sets _db_file_path_for_get_db
        logger.error("Database file path not set. Using default 'db.json'.")
        target_db_path = 'db.json'

    # Update the global path if a new one was explicitly passed via argument (e.g. from test setup)
    if db_file_path_from_arg:
        _db_file_path_for_get_db = db_file_path_from_arg

    current_storage_path = None
    if db and db._storage:
        current_storage_path = db._storage.path

    if db is None or current_storage_path != target_db_path:
        if db:
            db.close()
        logger.info(f"Initializing TinyDB with file: {target_db_path}")
        db = TinyDB(target_db_path)
    return db

mcp = FastMCP()

def _build_query(query_params: dict) -> Query | None:
    """
    Builds a TinyDB Query object from a dictionary of parameters.
    Combines parameters with logical AND.
    Returns None if query_params is empty or None.
    """
    if not query_params:
        return None

    final_query: Query | None = None
    for key, value in query_params.items():
        current_condition = (Query()[key] == value)
        if final_query is None:
            final_query = current_condition
        else:
            final_query &= current_condition
    return final_query

@mcp.tool()
def create_table(table_name: str) -> str:
    """Creates a new table in the database.

    Args:
        table_name: The name of the table to create.

    Returns:
        A confirmation message.
    """
    current_db = get_db()
    current_db.table(table_name)
    return f"Table '{table_name}' created successfully."

@mcp.tool()
def insert_document(table_name: str, document: dict) -> str:
    """Inserts a document into the specified table.

    Args:
        table_name: The name of the table.
        document: The document to insert.

    Returns:
        The ID of the inserted document.
    """
    current_db = get_db()
    table = current_db.table(table_name)
    doc_id = table.insert(document)
    return str(doc_id)

@mcp.tool()
def query_documents(table_name: str, query_params: dict = None) -> str:
    """Queries documents from the specified table.

    Args:
        table_name: The name of the table.
        query_params: Optional. A dictionary of field-value pairs for exact matches.
                      Example: {"name": "John", "age": 30}

    Returns:
        A JSON string list of matching documents.
    """
    current_db = get_db()
    table = current_db.table(table_name)
    db_query = _build_query(query_params)

    if db_query is not None:
        results = table.search(db_query)
    else:
        results = table.all()
    return json.dumps(results)

@mcp.tool()
def update_documents(table_name: str, query_params: dict, update_data: dict) -> str:
    """Updates documents in the specified table.

    Args:
        table_name: The name of the table.
        query_params: A dictionary of field-value pairs to identify documents to update.
        update_data: A dictionary of field-value pairs to update.

    Returns:
        The number of updated documents.
    """
    current_db = get_db()
    table = current_db.table(table_name)
    db_query = _build_query(query_params)

    if db_query is None:
        return "Error: Query parameters are required for update operations."

    updated_ids = table.update(update_data, db_query)
    return str(len(updated_ids))


@mcp.tool()
def delete_documents(table_name: str, query_params: dict) -> str:
    """Deletes documents from the specified table.

    Args:
        table_name: The name of the table.
        query_params: A dictionary of field-value pairs to identify documents to delete.

    Returns:
        The number of deleted documents.
    """
    current_db = get_db()
    table = current_db.table(table_name)
    db_query = _build_query(query_params)

    if db_query is None:
        return "Error: Query parameters are required for delete operations."

    deleted_ids = table.remove(db_query)
    return str(len(deleted_ids))

@mcp.tool()
def purge_table(table_name: str) -> str:
    """Removes all documents from the specified table.

    Args:
        table_name: The name of the table to purge.

    Returns:
        A confirmation message.
    """
    current_db = get_db()
    table = current_db.table(table_name)
    table.truncate()
    return f"Table '{table_name}' purged successfully."

@mcp.tool()
def drop_table(table_name: str) -> str:
    """Drops the specified table from the database.

    Args:
        table_name: The name of the table to drop.

    Returns:
        A confirmation message.
    """
    current_db = get_db()
    current_db.drop_table(table_name)
    return f"Table '{table_name}' dropped successfully."

def server_main():
    parser = argparse.ArgumentParser(description="MCP TinyDB Server")
    parser.add_argument(
        "--db-file",
        type=str,
        default="db.json",
        help="Path to the TinyDB JSON file.",
    )
    args = parser.parse_args(sys.argv[1:])  # Use only arguments after script name

    global _db_file_path_for_get_db
    _db_file_path_for_get_db = args.db_file

    logger.info(f"Starting tinydb-server. Database file: {args.db_file}")

    get_db(args.db_file)

    mcp.run('stdio')

if __name__ == "__main__":
    server_main()