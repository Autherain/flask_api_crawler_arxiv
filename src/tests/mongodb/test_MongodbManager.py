import pytest
from flask_api_crawler_arxiv.mongodb.MongodbManager import MongoDBManager
from flask_api_crawler_arxiv.flask_api.app import application
from unittest.mock import MagicMock
from bson import ObjectId


@pytest.fixture
def client():
    application.config["TESTING"] = True
    application.config["DEBUG"] = False

    # Mock MongoDBManager
    mongodb_manager_mock = MagicMock(spec=MongoDBManager)
    MongoDBManager.return_value = mongodb_manager_mock

    with application.test_client() as client:
        yield client


def test_insert_and_retrieve_article(client):
    # Mock MongoDB connection
    mongodb_manager_mock = MongoDBManager.return_value
    mongodb_manager_mock.client = MagicMock()
    mongodb_manager_mock.db = MagicMock()

    # Define a sample article for testing
    sample_article = {
        "header": "Test Article",
        "metadata": {
            "oai_dc:dc.date": "2023-01-01",
            "oai_dc:dc.subject": "Test Subject",
            # ... other metadata fields ...
        },
    }

    # Insert the sample article
    response = client.post("/articles", json=sample_article)
    assert response.status_code == 500

    # Retrieve the inserted article by ID
    inserted_id = response.json["id"]
    response = client.get(f"/article/{inserted_id}")
    assert response.status_code == 200
    assert response.json["header"] == "Test Article"
    assert response.json["metadata"]["oai_dc:dc.subject"] == "Test Subject"


def test_invalid_object_id_format(client):
    response = client.get("/article/invalid_id")
    assert response.status_code == 400
    assert response.json["error"] == "Invalid ObjectId format"


def test_article_not_found(client):
    # Mock MongoDB connection
    mongodb_manager_mock = MongoDBManager.return_value
    mongodb_manager_mock.client = MagicMock()
    mongodb_manager_mock.db = MagicMock()

    # Try to retrieve an article with a non-existent ID
    response = client.get("/article/60409e211c45b874f812589f")
    assert response.status_code == 404
    assert response.json["error"] == "Article not found"
