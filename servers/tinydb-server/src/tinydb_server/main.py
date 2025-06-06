from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
import logging
import os # Added import
from tinydb import TinyDB, Query, where

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger("tinydb-server")

# Initialize TinyDB
DB_FILE = os.getenv('MCP_TINYDB_FILE', 'db.json')
# db will be initialized by get_db() on first use or when DB_FILE changes.
db = None

def get_db():
    """Gets the TinyDB instance, re-initializes if DB_FILE changed or not initialized."""
    global db # Our global db instance
    # Access the global DB_FILE, which might be changed by tests
    # (Need to ensure global DB_FILE is accessible and modifiable)
    global DB_FILE

    current_storage_path = None
    if db and db._storage: # Check if db is initialized and has storage
        current_storage_path = db._storage.path

    if db is None or current_storage_path != DB_FILE:
        if db: # If db exists and path is different, close it
            db.close()
        db = TinyDB(DB_FILE) # Re-initialize with the potentially new DB_FILE
    return db

# Create the MCP server object
mcp = FastMCP()

@mcp.tool()
def create_table(table_name: str) -> TextContent:
    """Creates a new table in the database.

    Args:
        table_name: The name of the table to create.

    Returns:
        A confirmation message.
    """
    current_db = get_db()
    current_db.table(table_name)
    return TextContent(text=f"Table '{table_name}' created successfully.")

@mcp.tool()
def insert_document(table_name: str, document: dict) -> TextContent:
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
    return TextContent(text=str(doc_id))

@mcp.tool()
def query_documents(table_name: str, query_params: dict = None) -> TextContent:
    """Queries documents from the specified table.

    Args:
        table_name: The name of the table.
        query_params: Optional. A dictionary of field-value pairs for exact matches.
                      Example: {"name": "John", "age": 30}

    Returns:
        A list of matching documents.
    """
    current_db = get_db()
    table = current_db.table(table_name)
    if query_params:
        # Simple query construction for exact matches
        # For more complex queries, this part would need to be more sophisticated
        # and potentially use `where()` syntax more directly.
        condition = None
        for key, value in query_params.items():
            if condition is None:
                condition = (Query()[key] == value)
            else:
                condition &= (Query()[key] == value)
        if condition is not None:
            results = table.search(condition)
        else: # query_params was empty
            results = table.all()
    else:
        results = table.all()
    return TextContent(text=str(results))

@mcp.tool()
def update_documents(table_name: str, query_params: dict, update_data: dict) -> TextContent:
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
    condition = None
    for key, value in query_params.items():
        if condition is None:
            condition = (Query()[key] == value)
        else:
            condition &= (Query()[key] == value)

    if condition is not None:
        updated_count = table.update(update_data, condition)
    else: # No query_params provided, should not happen based on signature but handle defensively
        return TextContent(text="Error: query_params cannot be empty for update.")

    return TextContent(text=str(len(updated_count)))


@mcp.tool()
def delete_documents(table_name: str, query_params: dict) -> TextContent:
    """Deletes documents from the specified table.

    Args:
        table_name: The name of the table.
        query_params: A dictionary of field-value pairs to identify documents to delete.

    Returns:
        The number of deleted documents.
    """
    current_db = get_db()
    table = current_db.table(table_name)
    condition = None
    for key, value in query_params.items():
        if condition is None:
            condition = (Query()[key] == value)
        else:
            condition &= (Query()[key] == value)

    if condition is not None:
        deleted_ids = table.remove(condition)
    else: # No query_params provided, should not happen based on signature but handle defensively
        return TextContent(text="Error: query_params cannot be empty for delete.")

    return TextContent(text=str(len(deleted_ids)))

@mcp.tool()
def purge_table(table_name: str) -> TextContent:
    """Removes all documents from the specified table.

    Args:
        table_name: The name of the table to purge.

    Returns:
        A confirmation message.
    """
    current_db = get_db()
    table = current_db.table(table_name)
    table.truncate()
    return TextContent(text=f"Table '{table_name}' purged successfully.")

@mcp.tool()
def drop_table(table_name: str) -> TextContent:
    """Drops the specified table from the database.

    Args:
        table_name: The name of the table to drop.

    Returns:
        A confirmation message.
    """
    current_db = get_db()
    current_db.drop_table(table_name)
    return TextContent(text=f"Table '{table_name}' dropped successfully.")

# This is the main entry point for your server
def main():
    logger.info('Starting tinydb-server')
    get_db() # Initialize db on start
    mcp.run('stdio')

if __name__ == "__main__":
    main()