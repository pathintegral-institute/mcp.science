import unittest
import os
import sys
import json # Added import
from tinydb import TinyDB, Query

# Add the src directory to sys.path to allow importing tinydb_server
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from tinydb_server import main as tinydb_main_module # For accessing module's global 'db'
from tinydb_server.main import (
    get_db, # For calling directly
    create_table,
    insert_document,
    query_documents,
    update_documents,
    delete_documents,
    purge_table,
    drop_table
)

class TestTinyDBServer(unittest.TestCase):

    def setUp(self):
        """Set up for test methods."""
        self.test_db_file = 'test_db.json'
        # Call get_db() with the test_db_file path.
        # This will ensure the db instance in main (the module) uses this file
        # and also sets the internal _db_file_path_for_get_db for subsequent calls within tools.
        get_db(db_file_path_from_arg=self.test_db_file)

    def tearDown(self):
        """Tear down after test methods."""
        # Access the global db instance from the imported module and manage it
        if tinydb_main_module.db:
            tinydb_main_module.db.close()
            tinydb_main_module.db = None # Ensure it's reset for the next test
        try:
            os.remove(self.test_db_file)
        except FileNotFoundError:
            pass # File might not have been created by all tests

    def test_create_table(self):
        table_name = "test_table_creation"
        # 1. Call create_table (uses the module's global db)
        response = create_table(table_name)
        self.assertEqual(response, f"Table '{table_name}' created successfully.")

        # 2. Use the module's db to insert and then remove a dummy record
        #    to ensure the table is physically represented in the JSON file.
        m_db = tinydb_main_module.get_db() # Should be the same instance
        self.assertIsNotNone(m_db, "Module DB should be initialized")
        table_instance = m_db.table(table_name)
        doc_id = table_instance.insert({'_test_creation': True})
        table_instance.remove(doc_ids=[doc_id])

        # 3. Close the module's db to flush changes.
        if tinydb_main_module.db:
            tinydb_main_module.db.close()
            tinydb_main_module.db = None # Reset for next test via setUp

        # 4. Verify with a separate TinyDB instance.
        with TinyDB(self.test_db_file) as verify_db:
            self.assertTrue(table_name in verify_db.tables(),
                            f"Table '{table_name}' should exist in file after creation and dummy insert/delete.")

    def test_insert_document(self):
        table_name = "insert_test"
        create_table(table_name)
        doc = {"name": "test_doc", "value": 123}
        response = insert_document(table_name, doc)
        # Make sure the response is a digit string before int conversion for doc_id
        self.assertTrue(response.isdigit())
        doc_id = int(response)

        with TinyDB(self.test_db_file) as verify_db:
            table = verify_db.table(table_name)
            retrieved_doc = table.get(doc_id=doc_id)
            self.assertIsNotNone(retrieved_doc)
            self.assertEqual(retrieved_doc['name'], "test_doc")

    def test_query_documents_all(self):
        table_name = "query_all_test"
        create_table(table_name)
        insert_document(table_name, {"id": 1, "data": "a"})
        insert_document(table_name, {"id": 2, "data": "b"})

        response = query_documents(table_name)
        results = json.loads(response)
        self.assertEqual(len(results), 2)

    def test_query_documents_with_params(self):
        table_name = "query_params_test"
        create_table(table_name)
        insert_document(table_name, {"name": "alpha", "value": 1})
        insert_document(table_name, {"name": "beta", "value": 2})
        insert_document(table_name, {"name": "alpha", "value": 3})

        response_query = query_documents(table_name, query_params={"name": "alpha"})
        results = json.loads(response_query)
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r['name'], 'alpha')

        response_val = query_documents(table_name, query_params={"value": 2})
        results_val = json.loads(response_val)
        self.assertEqual(len(results_val), 1)
        self.assertEqual(results_val[0]['name'], 'beta')

    def test_update_documents(self):
        table_name = "update_test"
        create_table(table_name)
        insert_document(table_name, {"name": "old_name", "value": 10})
        insert_document(table_name, {"name": "another_name", "value": 20})

        query_params = {"name": "old_name"}
        update_data = {"value": 15, "status": "updated"}
        response_update = update_documents(table_name, query_params, update_data)
        # Assuming the response is the count of updated documents as a string
        self.assertTrue(response_update.isdigit())
        updated_count = int(response_update)
        self.assertEqual(updated_count, 1)

        with TinyDB(self.test_db_file) as verify_db:
            table = verify_db.table(table_name)
            q = Query()
            updated_doc = table.get(q.name == "old_name")
            self.assertIsNotNone(updated_doc)
            self.assertEqual(updated_doc['value'], 15)
            self.assertEqual(updated_doc['status'], "updated")

            untouched_doc = table.get(q.name == "another_name")
            self.assertEqual(untouched_doc['value'], 20)

    def test_delete_documents(self):
        table_name = "delete_test"
        create_table(table_name)
        id1_resp = insert_document(table_name, {"key": "doc1"})
        id2_resp = insert_document(table_name, {"key": "doc2", "extra": "delete_me"})
        id3_resp = insert_document(table_name, {"key": "doc3", "extra": "delete_me"})

        query_params = {"extra": "delete_me"}
        response_delete = delete_documents(table_name, query_params)
        # Assuming the response is the count of deleted items as a string
        self.assertTrue(response_delete.isdigit())
        deleted_count = int(response_delete)
        self.assertEqual(deleted_count, 2)

        with TinyDB(self.test_db_file) as verify_db:
            table = verify_db.table(table_name)
            self.assertIsNotNone(table.get(doc_id=int(id1_resp))) # idX_resp are already string doc IDs
            self.assertIsNone(table.get(doc_id=int(id2_resp)))
            self.assertIsNone(table.get(doc_id=int(id3_resp)))

    def test_purge_table(self):
        table_name = "purge_test"
        create_table(table_name)
        insert_document(table_name, {"data": "something"})
        insert_document(table_name, {"data": "something_else"})

        response_purge = purge_table(table_name)
        self.assertEqual(response_purge, f"Table '{table_name}' purged successfully.")

        with TinyDB(self.test_db_file) as verify_db:
            table = verify_db.table(table_name)
            self.assertEqual(len(table.all()), 0)
            self.assertTrue(table_name in verify_db.tables())


    def test_drop_table(self):
        table_name = "drop_test_table" # Use a unique name
        # 1. Create the table
        create_table(table_name)

        # 2. Insert & remove a dummy document to ensure it's persisted for verification
        m_db_create = tinydb_main_module.get_db()
        table_instance_create = m_db_create.table(table_name)
        doc_id_create = table_instance_create.insert({'_test_drop_creation': True})
        table_instance_create.remove(doc_ids=[doc_id_create])

        # 3. Close the main db instance to flush
        if tinydb_main_module.db:
            tinydb_main_module.db.close()
            tinydb_main_module.db = None

        # 4. Verify table exists with a new instance
        with TinyDB(self.test_db_file) as verify_db_check:
            self.assertTrue(table_name in verify_db_check.tables(),
                            f"Table '{table_name}' should exist after creation and dummy ops.")

        # 5. Call drop_table (this will re-initialize tinydb_main_module.db via get_db())
        response_drop = drop_table(table_name)
        self.assertEqual(response_drop, f"Table '{table_name}' dropped successfully.")

        # 6. Close the main db instance again to flush the drop operation
        if tinydb_main_module.db:
            tinydb_main_module.db.close()
            tinydb_main_module.db = None

        # 7. Verify table does NOT exist with a new instance
        with TinyDB(self.test_db_file) as verify_db_after_drop:
            self.assertFalse(table_name in verify_db_after_drop.tables(),
                             f"Table '{table_name}' should NOT exist after drop and flush.")

if __name__ == '__main__':
    unittest.main()
