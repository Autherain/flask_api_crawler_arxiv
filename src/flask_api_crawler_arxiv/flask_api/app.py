import os
import logging

from bson import json_util
from bson.objectid import ObjectId
import platform
from datetime import datetime
from flask import Flask, jsonify, request, Response

from flask_api_crawler_arxiv.app_config_dict import app_config
from flask_api_crawler_arxiv.mongodb.MongodbManager import MongoDBManager

from flask_api_crawler_arxiv.python_cron.cron_inject_data_mongodb import (
    cron_inject_data_mongodb,
)

from flask_api_crawler_arxiv.utils.setup_logging import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

application = Flask(__name__)

db_manager = MongoDBManager(
    f'mongodb://{app_config["MONGO_INITDB_ROOT_USERNAME"]}:{app_config["MONGO_INITDB_ROOT_PASSWORD"]}@{app_config["MONGO_CONTAINER_NAME"]}:{app_config["MONGO_DOCKER_PORT"]}',
    f'{app_config["MONGO_INITDB_DATABASE"]}',
)


def return_pretty_json_from_bson(bson_data):
    """
    Serialize MongoDB objects to JSON format with proper indentation and headers.

    Args:
        bson_data: MongoDB data to be serialized.

    Returns:
        Response: Flask Response object containing formatted JSON data with appropriate headers.
    """
    # Use json_util to serialize MongoDB objects
    articles_list = json_util.dumps(bson_data, indent=4)
    # Set the response headers for JSON content
    response = Response(articles_list, content_type="application/json")
    response.headers["X-Content-Type-Options"] = "nosniff"

    return response


@application.route("/articles/", methods=["GET"])
def get_articles():
    """
    Endpoint to retrieve paginated articles.

    Returns:
        Response: Paginated articles in JSON format.
    """
    # Set a fixed per_page value
    per_page = 50  # Maximum entities per page

    # Get the page number from the URL or default to 1
    page = int(request.args.get("page", 1))

    # Extract query parameters for filtering
    description = request.args.get("description")
    title = request.args.get("title")
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")

    # Parse start_date and end_date if provided
    start_date = (
        datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
    )
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None

    # Define the transaction operation to retrieve filtered and paginated articles
    def get_filtered_articles_transaction(db):
        query = {}

        # Apply filters based on criteria
        if description:
            query["metadata.oai_dc:dc.dc:description"] = {
                "$regex": f".*{description}.*",
                "$options": "i",
            }

        if title:
            query["metadata.oai_dc:dc.dc:title"] = {
                "$regex": f".*{title}.*",
                "$options": "i",
            }

        if start_date and end_date:
            query["header.datestamp"] = {
                "$gte": start_date,
                "$lte": end_date,
            }

        articles_cursor = (
            db.arxiv_data_doc.find(query).skip((page - 1) * per_page).limit(per_page)
        )

        return return_pretty_json_from_bson(articles_cursor)

    # Perform the transaction
    try:
        db_manager.open_connection()
        response = db_manager.perform_transaction(get_filtered_articles_transaction)
        db_manager.close_connection()

        logger.info(" Retrieved filtered articles successfully")
        return response

    except Exception as e:
        logging.error(f"Error retrieving articles: {e}")
        return {"error": str(e)}, 500


@application.route("/article/<id>", methods=["GET"])
def get_article_by_id(id):
    """
    Endpoint to retrieve an article by its ID.

    Args:
        id (str): ObjectId of the article.

    Returns:
        Response: Article details in JSON format.
    """
    try:
        # Convert the provided ID to ObjectId
        obj_id = ObjectId(id)
    except Exception:
        logging.error("error" "Invalid ObjectId format")
        return jsonify({"error": "Invalid ObjectId format"}), 400

    # Define the transaction operation to retrieve the document by ObjectId
    def get_article_transaction(db):
        article = db.arxiv_data_doc.find_one({"_id": obj_id})
        if article:
            return return_pretty_json_from_bson(article)
        else:
            logging.error("error Article not found")
            return jsonify({"error": "Article not found"}), 404

    # Perform the transaction
    try:
        db_manager.open_connection()
        response = db_manager.perform_transaction(get_article_transaction)
        db_manager.close_connection()

        return response

    except Exception as e:
        logging.info(f"error {e}")
        return jsonify({"error": str(e)}), 500


@application.route("/inject_data_to_mongodb", methods=["GET"])
def inject_data_to_mongodb():
    """
    This route is responsible for injecting data into MongoDB based on the specified ARXSET parameter.

    Args:
        None

    Query Parameters:
        ARXSET (optional): The ARXSET parameter specifying the data to be injected. If nothing is specified then the API will extract from "cs" arxset.

    Returns:
        Response: Success or error message in JSON format.

    Raises:
        None, as the caught exception is logged and returned as part of the response.
    """
    try:
        arxset = request.args.get(
            "ARXSET", default="cs"
        )  # Get ARXSET from query parameters with default value None

        cron_inject_data_mongodb(app_config, arxset=arxset)
        return jsonify({"message": "Data injection completed successfully."})
    except Exception as e:
        error_message = f"Error during data injection: {str(e)}"
        logger.error(error_message)
        return jsonify({"error": error_message}), 500  # 500 Internal Server Error


@application.route("/text/<id>.txt", methods=["GET"])
def get_article_summary_by_id(id):
    """
    Endpoint to retrieve the summary of an article by its ID.

    Args:
        id (str): ObjectId of the article.

    Returns:
        Response: Article summary in JSON format.
    """
    try:
        # Convert the provided ID to ObjectId
        obj_id = ObjectId(id)
    except Exception:
        logging.error("error Invalid ObjectId format")
        return jsonify({"error": "Invalid ObjectId format"}), 400

    # Define the transaction operation to retrieve the document by ObjectId
    def get_article_summary_transaction(db):
        article = db.arxiv_data_doc.find_one(
            ({"_id": obj_id}, {"metadata.oai_dc:dc.dc:description": 1})
        )
        if article:
            logging.info("Id was successfully found")
            return return_pretty_json_from_bson(article)
        else:
            logging.info("error Article not found")
            return jsonify({"error": "Article not found"}), 404

    # Perform the transaction
    try:
        db_manager.open_connection()
        response = db_manager.perform_transaction(get_article_summary_transaction)
        db_manager.close_connection()

        return response

    except Exception as e:
        logging.error(f"error {e}")
        return jsonify({"error": str(e)}), 500


@application.route("/articles", methods=["POST"])
def insert_doc_from_user():
    """
    Endpoint to insert a new document from the user.

    Returns:
        Response: Success or error message in JSON format.
    """
    try:
        # Get the JSON document from the request body
        new_article = request.get_json()

        # Validate that the required fields are present in the document
        if not new_article or not all(
            key in new_article for key in ["header", "metadata"]
        ):
            logging.error("error Invalid or incomplete document")
            return jsonify({"error": "Invalid or incomplete document"}), 400

        # Define the transaction operation to insert the document into MongoDB
        def insert_article_transaction(db):
            result = db.arxiv_data_doc.insert_one(new_article)
            inserted_id = str(result.inserted_id)
            logging.info("Article inserted successfully")
            return (
                jsonify(
                    {"message": "Article inserted successfully", "id": inserted_id}
                ),
                201,
            )

        # Perform the transaction
        db_manager.open_connection()
        response = db_manager.perform_transaction(insert_article_transaction)
        db_manager.close_connection()

        return response

    except Exception as e:
        logging.error(f"error {e}")
        return jsonify({"error": str(e)}), 500


@application.route("/time")
def current_time():
    return f"Current Server Time: {datetime.now()}"


@application.route("/health")
def health_check():
    return "OK"


@application.route("/")
def welcome():
    return "Welcome to My Flask API!"


@application.route("/version")
def version():
    return f"My Flask API Version: 1.0\nPython Version: {platform.python_version()}"


@application.route("/umad_bra")
def umadbra():
    return r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠴⠤⠤⠴⠄⡄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣠⠄⠒⠉⠀⠀⠀⠀⠀⠀⠀⠀⠁⠃⠆⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⡜⠁⠀⠀⠀⢠⡄⠀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠑⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢈⠁⠀⠀⠠⣿⠿⡟⣀⡹⠆⡿⣃⣰⣆⣤⣀⠀⠀⠹⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣼⠀⠀⢀⣀⣀⣀⣀⡈⠁⠙⠁⠘⠃⠡⠽⡵⢚⠱⠂⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ___       _        _             _      
⠀⠀⠀⠀⠀⡆⠀⠀⠀⠀⢐⣢⣤⣵⡄⢀⠀⢀⢈⣉⠉⠉⠒⠤⠀⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  /___\_ __ | |_ ___ | | ___   __ _(_) ___ 
⠀⠀⠀⠀⠘⡇⠀⠀⠀⠀⠀⠉⠉⠁⠁⠈⠀⠸⢖⣿⣿⣷⠀⠀⢰⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ //  // '_ \| __/ _ \| |/ _ \ / _` | |/ _ \
⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⢀⠃⠀⡄⠀⠈⠉⠀⠀⠀⢴⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀/ \_//| | | | || (_) | | (_) | (_| | |  __/
⠀⠀⠀⠀⢈⣇⠀⠀⠀⠀⠀⠀⠀⢰⠉⠀⠀⠱⠀⠀⠀⠀⠀⢠⡄⠀⠀⠀⠀⠀⣀⠔⠒⢒⡩⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\___/ |_| |_|\__\___/|_|\___/ \__, |_|\___|
⠀⠀⠀⠀⣴⣿⣤⢀⠀⠀⠀⠀⠀⠈⠓⠒⠢⠔⠀⠀⠀⠀⠀⣶⠤⠄⠒⠒⠉⠁⠀⠀⠀⢸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀                              |___/
⡄⠤⠒⠈⠈⣿⣿⣽⣦⠀⢀⢀⠰⢰⣀⣲⣿⡐⣤⠀⠀⢠⡾⠃⠀⠀⠀⠀⠀⠀⠀⣀⡄⣠⣵⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠘⠏⢿⣿⡁⢐⠶⠈⣰⣿⣿⣿⣿⣷⢈⣣⢰⡞⠀⠀⠀⠀⠀⠀⢀⡴⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⢿⣿⣍⠀⠀⠸⣿⣿⣿⣿⠃⢈⣿⡎⠁⠀⠀⠀⠀⣠⠞⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⢙⣿⣆⠀⠀⠈⠛⠛⢋⢰⡼⠁⠁⠀⠀⠀⢀⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠚⣷⣧⣷⣤⡶⠎⠛⠁⠀⠀⠀⢀⡤⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠈⠁⠀⠀⠀⠀⠀⠠⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    application.run(host="0.0.0.0", port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
