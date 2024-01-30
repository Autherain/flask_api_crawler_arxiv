import logging
from pymongo import MongoClient

from flask_api_crawler_arxiv.utils.setup_logging import setup_logging


class MongoDBManager:
    """
    MongoDBManager class for managing MongoDB connections and transactions.
    ... (rest of the class remains unchanged)

    """

    def __init__(self, connection_string, database_name):
        """
        Initialize MongoDBManager with the provided connection string and database name.

        Args:
            connection_string (str): MongoDB connection string.
            database_name (str): Name of the MongoDB database.
        """
        setup_logging()
        self._logging = logging.getLogger(__name__)

        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None

    def open_connection(self):
        """
        Open the MongoDB client connection.
        """
        self.client = MongoClient(self.connection_string)
        self.db = self.client[self.database_name]
        self._logging.info("MongoDB connection opened.")

    def close_connection(self):
        """
        Close the MongoDB client connection.
        """
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self._logging.info("MongoDB connection closed.")

    def perform_transaction(self, transaction_operations):
        """
        Perform a transaction with the given operations.

        Args:
            transaction_operations (function): Function that takes a MongoDB database object
                                              and performs transactional operations.

        Raises:
            Exception: If an error occurs during the transaction, it will be raised.

        Example:
            manager = MongoDBManager("your_mongodb_connection_string", "your_database_name")
            manager.open_connection()
            try:
                manager.perform_transaction(lambda db: db.collection.insert_one({"field": "value"}))
                self._logging.info("Transaction successful.")
            finally:
                manager.close_connection()
        """
        with self.client.start_session() as session:
            with session.start_transaction():
                try:
                    result = transaction_operations(self.db)
                    return result
                except Exception as e:
                    session.abort_transaction()
                    self._logging.error(f"Transaction failed: {str(e)}")
                    raise e
