import unittest
import os
import sys
from tinydb import TinyDB, Query

# Add the src directory to sys.path to allow importing tinydb_server
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from tinydb_server import main as tinydb_main

class TestTinyDBServer(unittest.TestCase):

    def setUp(self):
        """Set up for test methods."""
        self.test_db_file = 'test_db.json'
        # Call get_db() with the test_db_file path.
        # This will ensure the db instance in tinydb_main uses this file
        # and also sets the internal _db_file_path_for_get_db for subsequent calls within tools.
        tinydb_main.get_db(db_file_path_from_arg=self.test_db_file)

    def tearDown(self):
        """Tear down after test methods."""
        current_db = tinydb_main.get_db() # Get current instance
        if current_db: # Check if it's not None
            current_db.close()
        try:
            os.remove(self.test_db_file)
        except FileNotFoundError:
            pass # File might not have been created by all tests

    def test_create_table(self):
        table_name = "test_table"
        response = tinydb_main.create_table(table_name)
        self.assertEqual(response.text, f"Table '{table_name}' created successfully.")
        # Verify directly
        # Use tinydb_main.get_db() to ensure consistency if direct TinyDB checks are needed,
        # or open a separate TinyDB instance on self.test_db_file for verification.
        # For simplicity and direct verification, opening a new instance is fine.
        with TinyDB(self.test_db_file) as verify_db:
            self.assertTrue(table_name in verify_db.tables())

    def test_insert_document(self):
        table_name = "insert_test"
        tinydb_main.create_table(table_name)
        doc = {"name": "test_doc", "value": 123}
        response = tinydb_main.insert_document(table_name, doc)
        doc_id = int(response.text)

        with TinyDB(self.test_db_file) as verify_db:
            table = verify_db.table(table_name)
            retrieved_doc = table.get(doc_id=doc_id)
            self.assertIsNotNone(retrieved_doc)
            self.assertEqual(retrieved_doc['name'], "test_doc")

    def test_query_documents_all(self):
        table_name = "query_all_test"
        tinydb_main.create_table(table_name)
        tinydb_main.insert_document(table_name, {"id": 1, "data": "a"})
        tinydb_main.insert_document(table_name, {"id": 2, "data": "b"})

        response = tinydb_main.query_documents(table_name)
        results = eval(response.text)
        self.assertEqual(len(results), 2)

    def test_query_documents_with_params(self):
        table_name = "query_params_test"
        tinydb_main.create_table(table_name)
        tinydb_main.insert_document(table_name, {"name": "alpha", "value": 1})
        tinydb_main.insert_document(table_name, {"name": "beta", "value": 2})
        tinydb_main.insert_document(table_name, {"name": "alpha", "value": 3})

        response = tinydb_main.query_documents(table_name, query_params={"name": "alpha"})
        results = eval(response.text)
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r['name'], 'alpha')

        response_val = tinydb_main.query_documents(table_name, query_params={"value": 2})
        results_val = eval(response_val.text)
        self.assertEqual(len(results_val), 1)
        self.assertEqual(results_val[0]['name'], 'beta')

    def test_update_documents(self):
        table_name = "update_test"
        tinydb_main.create_table(table_name)
        tinydb_main.insert_document(table_name, {"name": "old_name", "value": 10})
        tinydb_main.insert_document(table_name, {"name": "another_name", "value": 20})

        query_params = {"name": "old_name"}
        update_data = {"value": 15, "status": "updated"}
        response = tinydb_main.update_documents(table_name, query_params, update_data)
        updated_count = int(response.text)
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
        tinydb_main.create_table(table_name)
        id1_resp = tinydb_main.insert_document(table_name, {"key": "doc1"})
        id2_resp = tinydb_main.insert_document(table_name, {"key": "doc2", "extra": "delete_me"})
        id3_resp = tinydb_main.insert_document(table_name, {"key": "doc3", "extra": "delete_me"})

        query_params = {"extra": "delete_me"}
        response = tinydb_main.delete_documents(table_name, query_params)
        deleted_count = int(response.text)
        self.assertEqual(deleted_count, 2)

        with TinyDB(self.test_db_file) as verify_db:
            table = verify_db.table(table_name)
            self.assertIsNotNone(table.get(doc_id=int(id1_resp.text)))
            self.assertIsNone(table.get(doc_id=int(id2_resp.text)))
            self.assertIsNone(table.get(doc_id=int(id3_resp.text)))

    def test_purge_table(self):
        table_name = "purge_test"
        tinydb_main.create_table(table_name)
        tinydb_main.insert_document(table_name, {"data": "something"})
        tinydb_main.insert_document(table_name, {"data": "something_else"})

        response = tinydb_main.purge_table(table_name)
        self.assertEqual(response.text, f"Table '{table_name}' purged successfully.")

        with TinyDB(self.test_db_file) as verify_db:
            table = verify_db.table(table_name)
            self.assertEqual(len(table.all()), 0)
            self.assertTrue(table_name in verify_db.tables())


    def test_drop_table(self):
        table_name = "drop_test"
        tinydb_main.create_table(table_name)
        with TinyDB(self.test_db_file) as verify_db_check: # Corrected variable name
            self.assertTrue(table_name in verify_db_check.tables())

        response = tinydb_main.drop_table(table_name)
        self.assertEqual(response.text, f"Table '{table_name}' dropped successfully.")

        with TinyDB(self.test_db_file) as verify_db:
            self.assertFalse(table_name in verify_db.tables())

if __name__ == '__main__':
    unittest.main()
