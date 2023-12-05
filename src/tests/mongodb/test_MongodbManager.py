import pytest
from unittest.mock import MagicMock
from flask_api_crawler_arxiv.mongodb.MongodbManager import (
    MongoDBManager,
)  # Replace 'your_module' with the actual module name


@pytest.fixture
def mongo_manager():
    connection_string = "mongodb://mongodbuser:your_mongodb_root_password@localhost:27017"
    database_name = "flaskdb"
    manager = MongoDBManager(connection_string, database_name)
    yield manager
    manager.close_connection()


def test_open_connection(mongo_manager):
    assert mongo_manager.client is None
    assert mongo_manager.db is None

    mongo_manager.open_connection()

    assert mongo_manager.client is not None
    assert mongo_manager.db is not None


def test_close_connection(mongo_manager):
    mongo_manager.open_connection()
    assert mongo_manager.client is not None

    mongo_manager.close_connection()

    assert mongo_manager.client is None
    assert mongo_manager.db is None


def test_perform_transaction(mongo_manager):
    mock_operations = MagicMock()

    mongo_manager.open_connection()

    # Perform a successful transaction
    mongo_manager.perform_transaction(mock_operations)

    # Ensure that the transaction_operations function was called
    mock_operations.assert_called_once_with(mongo_manager.db)


def test_perform_transaction_with_exception(mongo_manager):
    mock_operations = MagicMock(side_effect=Exception("Test exception"))

    mongo_manager.open_connection()

    # Perform a transaction with an exception
    with pytest.raises(Exception, match="Test exception"):
        mongo_manager.perform_transaction(mock_operations)

    # Ensure that the transaction_operations function was called
    mock_operations.assert_called_once_with(mongo_manager.db)
