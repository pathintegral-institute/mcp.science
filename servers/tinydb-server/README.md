# TinyDB Server

This server uses TinyDB to store and retrieve data. It demonstrates how to use the MCP server with a TinyDB backend.

## Features

The server provides the following functions to interact with a TinyDB database:

-   **`create_table(table_name: str)`**
    -   Purpose: Creates a new table in the database.
    -   Arguments:
        -   `table_name` (str): The name of the table to create.
    -   Returns: (TextContent) A confirmation message.

-   **`insert_document(table_name: str, document: dict)`**
    -   Purpose: Inserts a document into the specified table.
    -   Arguments:
        -   `table_name` (str): The name of the table.
        -   `document` (dict): The document to insert (must be a JSON serializable dictionary).
    -   Returns: (TextContent) The ID of the inserted document as a string.

-   **`query_documents(table_name: str, query_params: dict = None)`**
    -   Purpose: Queries documents from the specified table.
    -   Arguments:
        -   `table_name` (str): The name of the table.
        -   `query_params` (dict, optional): A dictionary of field-value pairs for exact matches. If not provided or empty, all documents are returned.
    -   Returns: (TextContent) A string representation of a list of matching documents.

-   **`update_documents(table_name: str, query_params: dict, update_data: dict)`**
    -   Purpose: Updates documents in the specified table that match the query.
    -   Arguments:
        -   `table_name` (str): The name of the table.
        -   `query_params` (dict): A dictionary of field-value pairs to identify documents to update.
        -   `update_data` (dict): A dictionary of field-value pairs to apply as updates.
    -   Returns: (TextContent) The number of updated documents as a string.

-   **`delete_documents(table_name: str, query_params: dict)`**
    -   Purpose: Deletes documents from the specified table that match the query.
    -   Arguments:
        -   `table_name` (str): The name of the table.
        -   `query_params` (dict): A dictionary of field-value pairs to identify documents to delete.
    -   Returns: (TextContent) The number of deleted documents as a string.

-   **`purge_table(table_name: str)`**
    -   Purpose: Removes all documents from the specified table (truncates the table).
    -   Arguments:
        -   `table_name` (str): The name of the table to purge.
    -   Returns: (TextContent) A confirmation message.

-   **`drop_table(table_name: str)`**
    -   Purpose: Drops the specified table from the database.
    -   Arguments:
        -   `table_name` (str): The name of the table to drop.
    -   Returns: (TextContent) A confirmation message.

## Usage

Here's an example of how to interact with the server. The AI would call these functions sequentially.

1.  **Create a table named 'users':**
    ```json
    {
      "tool_name": "create_table",
      "arguments": {
        "table_name": "users"
      }
    }
    ```
    Server returns: `Table 'users' created successfully.`

2.  **Insert a user document:**
    ```json
    {
      "tool_name": "insert_document",
      "arguments": {
        "table_name": "users",
        "document": {
          "name": "Alice",
          "age": 30,
          "city": "Wonderland"
        }
      }
    }
    ```
    Server returns the ID of the new document, e.g., `1`.

3.  **Insert another user:**
    ```json
    {
      "tool_name": "insert_document",
      "arguments": {
        "table_name": "users",
        "document": {
          "name": "Bob",
          "age": 24,
          "city": "Builderland"
        }
      }
    }
    ```
    Server returns the ID, e.g., `2`.

4.  **Query for users named 'Alice':**
    ```json
    {
      "tool_name": "query_documents",
      "arguments": {
        "table_name": "users",
        "query_params": {
          "name": "Alice"
        }
      }
    }
    ```
    Server returns: `[{'name': 'Alice', 'age': 30, 'city': 'Wonderland', 'doc_id': 1}]` (actual format might vary based on TextContent structure)

5.  **Update Alice's age:**
    ```json
    {
      "tool_name": "update_documents",
      "arguments": {
        "table_name": "users",
        "query_params": { "name": "Alice" },
        "update_data": { "age": 31 }
      }
    }
    ```
    Server returns: `1` (number of documents updated).

6.  **Delete Bob:**
    ```json
    {
      "tool_name": "delete_documents",
      "arguments": {
        "table_name": "users",
        "query_params": { "name": "Bob" }
      }
    }
    ```
    Server returns: `1` (number of documents deleted).

7.  **Query all remaining users (should be just Alice):**
    ```json
    {
      "tool_name": "query_documents",
      "arguments": {
        "table_name": "users"
      }
    }
    ```
    Server returns: `[{'name': 'Alice', 'age': 31, 'city': 'Wonderland', 'doc_id': 1}]`

8.  **Purge the 'users' table:**
    ```json
    {
      "tool_name": "purge_table",
      "arguments": {
        "table_name": "users"
      }
    }
    ```
    Server returns: `Table 'users' purged successfully.`

9.  **Drop the 'users' table:**
    ```json
    {
      "tool_name": "drop_table",
      "arguments": {
        "table_name": "users"
      }
    }
    ```
    Server returns: `Table 'users' dropped successfully.`

## Running the Server

To run this server, you need to have Python 3.12 or higher installed.

First, navigate to the `servers/tinydb-server` directory and install the dependencies:

```bash
pip install -e .
```

Then, run the server from that directory.

To use the default database file (`db.json` in the current directory):
```bash
tinydb-server
```

To specify a custom database file path, use the `--db-file` argument:
```bash
tinydb-server --db-file /path/to/your/custom_database.json
```
Or, for a file in the current directory:
```bash
tinydb-server --db-file my_data.json
```

This will start the server and make it available for the MCP to connect to via stdio.
The server will create the database file if it doesn't already exist at the specified path.
