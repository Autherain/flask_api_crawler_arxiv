import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from flask_api_crawler_arxiv.flask_api.app import application
from flask_api_crawler_arxiv.mongodb.MongodbManager import MongoDBManager

from flask_api_crawler_arxiv.app_config_dict import app_config

# Fixture to override the MongoDBManager during tests


@pytest.fixture
def mock_db_manager():
    with patch(
        "flask_api_crawler_arxiv.flask_api.app.db_manager", autospec=True
    ) as mock_manager:
        yield mock_manager


# Fixture to create a test client for the Flask application
@pytest.fixture
def client():
    application.config["TESTING"] = True
    with application.test_client() as client:
        yield client


# Sample test for the get_articles endpoint
def test_get_articles(client, mock_db_manager):
    # Mock the perform_transaction method to return a sample list of articles
    mock_db_manager.perform_transaction.return_value = (
        [{"title": "Test Article"}],
        200,
    )

    # Send a GET request to the /articles/ endpoint
    response = client.get("/articles/")

    # Assert the response status code and content
    assert response.status_code == 200
    assert b"Test Article" in response.data


# Sample test for the insert_doc_from_user endpoint
def test_insert_doc_from_user(client, mock_db_manager):
    # Mock the perform_transaction method to return a success message
    mock_db_manager.perform_transaction.return_value = (
        {"message": "Article inserted successfully", "id": "123"},
        201,
    )

    # Send a POST request to the /articles endpoint with a sample JSON document
    response = client.post("/articles", json={"header": {}, "metadata": {}})

    # Assert the response status code and content
    assert response.status_code == 201
    assert b"Article inserted successfully" in response.data


def test_get_article_by_id(client, mock_db_manager):
    # Mock the perform_transaction method to return a sample article
    mock_db_manager.perform_transaction.return_value = (
        {"title": "Test Article", "_id": "123"},
        200,
    )

    # Send a GET request to the /article/<id> endpoint
    response = client.get("/article/657dd0d2253a61b7d7eefff8")

    # Assert the response status code and content
    assert response.status_code == 200
    assert b"Test Article" in response.data


def test_get_article_summary_by_id(client, mock_db_manager):
    # Mock the perform_transaction method to return a sample article summary
    mock_db_manager.perform_transaction.return_value = (
        {"metadata": {"oai_dc:dc:dc:description": "Summary"}},
        200,
    )

    # Send a GET request to the /text/<id>.txt endpoint
    response = client.get("/text/657dd0d2253a61b7d7eefff8.txt")

    # Assert the response status code and content
    assert response.status_code == 200
    assert b"Summary" in response.data


def test_health_check(client):
    # Send a GET request to the /health endpoint
    response = client.get("/health")

    # Assert the response status code and content
    assert response.status_code == 200
    assert b"OK" in response.data


def test_welcome(client):
    # Send a GET request to the / endpoint
    response = client.get("/")

    # Assert the response status code and content
    assert response.status_code == 200
    assert b"Welcome to My Flask API!" in response.data


def test_version(client):
    # Send a GET request to the /version endpoint
    response = client.get("/version")

    # Assert the response status code and content
    assert response.status_code == 200
    assert b"My Flask API Version: 1.0" in response.data
    assert b"Python Version:" in response.data


def test_get_articles_error_handling(client, mock_db_manager):
    # Mock the perform_transaction method to raise an exception
    mock_db_manager.perform_transaction.side_effect = Exception("Sample error")

    # Send a GET request to the /articles/ endpoint
    response = client.get("/articles/")

    # Assert the response status code and error message
    assert response.status_code == 500
    assert b"Sample error" in response.data


def test_insert_doc_from_user_error_handling(client, mock_db_manager):
    # Mock the perform_transaction method to raise an exception
    mock_db_manager.perform_transaction.side_effect = Exception("Sample error")

    # Send a POST request to the /articles endpoint with a sample JSON document
    response = client.post("/articles", json={"header": {}, "metadata": {}})

    # Assert the response status code and error message
    assert response.status_code == 500
    assert b"Sample error" in response.data


def test_get_article_by_id_error_handling(client, mock_db_manager):
    # Mock the perform_transaction method to raise an exception
    mock_db_manager.perform_transaction.side_effect = Exception("Sample error")

    # Send a GET request to the /article/<id> endpoint
    response = client.get("/article/657dd0d2253a61b7d7eefff8")

    # Assert the response status code and error message
    assert response.status_code == 500
    assert b"Sample error" in response.data


def test_get_article_summary_by_id_error_handling(client, mock_db_manager):
    # Mock the perform_transaction method to raise an exception
    mock_db_manager.perform_transaction.side_effect = Exception("Sample error")

    # Send a GET request to the /text/<id>.txt endpoint
    response = client.get("/text/657dd0d2253a61b7d7eefff8.txt")

    # Assert the response status code and error message
    assert response.status_code == 500
    assert b"Sample error" in response.data


def test_inject_data_to_mongodb(client, mock_db_manager):
    # Mock the cron_inject_data_mongodb function
    with patch(
        "flask_api_crawler_arxiv.flask_api.app.cron_inject_data_mongodb"
    ) as mock_cron:
        # Send a GET request to the /inject_data_to_mongodb endpoint
        response = client.get("/inject_data_to_mongodb?ARXSET=test_arxset")

        # Assert the response status code and success message
        assert response.status_code == 200
        assert b"Data injection completed successfully." in response.data

        # Assert that the cron_inject_data_mongodb function was called with the correct arguments
        mock_cron.assert_called_once_with(app_config, arxset="test_arxset")
