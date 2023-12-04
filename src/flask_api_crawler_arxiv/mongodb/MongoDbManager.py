from pymongo import MongoClient

class MongoDBManager:
    """
    MongoDBManager class for managing MongoDB connections and transactions.

    Attributes:
        connection_string (str): MongoDB connection string.
        database_name (str): Name of the MongoDB database.
        client: MongoClient instance for handling the connection to MongoDB.
        db: MongoDB database object.

    Methods:
        __init__: Initializes MongoDBManager with the provided connection string and database name.
        open_connection: Opens the MongoDB client connection.
        close_connection: Closes the MongoDB client connection.
        perform_transaction: Performs a transaction with the given operations.

    Usage:
        manager = MongoDBManager("your_mongodb_connection_string", "your_database_name")
        manager.open_connection()
        manager.perform_transaction(lambda db: db.collection.insert_one({"field": "value"}))
        manager.close_connection()
    """

    def __init__(self, connection_string, database_name):
        """
        Initialize MongoDBManager with the provided connection string and database name.

        Args:
            connection_string (str): MongoDB connection string.
            database_name (str): Name of the MongoDB database.
        """
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

    def close_connection(self):
        """
        Close the MongoDB client connection.
        """
        self.client.close()

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
            manager.perform_transaction(lambda db: db.collection.insert_one({"field": "value"}))
            manager.close_connection()
        """
        with self.client.start_session() as session:
            with session.start_transaction():
                try:
                    transaction_operations(self.db)
                except Exception as e:
                    session.abort_transaction()
                    raise e
