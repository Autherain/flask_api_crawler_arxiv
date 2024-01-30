import unittest
from unittest.mock import MagicMock, patch
import pytest
from flask_api_crawler_arxiv.utils.setup_logging import setup_logging
from flask_api_crawler_arxiv.mongodb.MongodbManager import (
    MongoDBManager,
)  # Replace 'your_module' with the actual module name


class TestMongoDBManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_logging()

    @pytest.fixture
    def mongo_manager_fixture(self, request):
        # Fixture for creating an instance of MongoDBManager with a mocked MongoClient
        connection_string = "mocked_connection_string"
        database_name = "mocked_database_name"

        # Patching MongoClient to return a MagicMock instance
        with patch("your_module.MongoClient") as mock_mongo_client:
            mock_client = MagicMock()
            mock_mongo_client.return_value = mock_client
            manager = MongoDBManager(connection_string, database_name)
            manager.open_connection()  # Open the connection for testing

            # Cleanup after the test
            def close_connection():
                manager.close_connection()

            request.addfinalizer(close_connection)

            return manager

    def test_open_connection(self):
        # Ensure open_connection() opens the connection and sets client and db attributes
        connection_string = "mocked_connection_string"
        database_name = "mocked_database_name"
        manager = MongoDBManager(connection_string, database_name)

        manager.open_connection()

        self.assertIsNotNone(manager.client)
        self.assertIsNotNone(manager.db)

    def test_close_connection(self):
        # Ensure close_connection() closes the connection and sets client and db to None
        connection_string = "mocked_connection_string"
        database_name = "mocked_database_name"
        manager = MongoDBManager(connection_string, database_name)
        manager.open_connection()

        manager.close_connection()

        self.assertIsNone(manager.client)
        self.assertIsNone(manager.db)

    def test_perform_transaction_success(self):
        # Ensure perform_transaction() executes successfully
        connection_string = "mocked_connection_string"
        database_name = "mocked_database_name"
        manager = MongoDBManager(connection_string, database_name)

        def mock_transaction_operations(db):
            return "Mocked result"

        with patch.object(manager, "client", MagicMock()), patch.object(
            manager, "db", MagicMock()
        ):
            result = manager.perform_transaction(mock_transaction_operations)

        self.assertEqual(result, "Mocked result")

    def test_perform_transaction_failure(self):
        # Ensure perform_transaction() handles transaction failure
        connection_string = "mocked_connection_string"
        database_name = "mocked_database_name"
        manager = MongoDBManager(connection_string, database_name)

        def mock_transaction_operations(db):
            raise Exception("Mocked transaction failure")

        with patch.object(manager, "client", MagicMock()), patch.object(
            manager, "db", MagicMock()
        ):
            with self.assertRaises(Exception):
                manager.perform_transaction(mock_transaction_operations)

        # Ensure the session is aborted and the connection is closed
        self.assertIsNone(manager.client)
        self.assertIsNone(manager.db)


if __name__ == "__main__":
    unittest.main()
