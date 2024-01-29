import logging
from datetime import date

from flask_api_crawler_arxiv.mongodb.MongodbManager import MongoDBManager
from flask_api_crawler_arxiv.arxiv_services.RecordConverterOAI import RecordConverterOAI
from flask_api_crawler_arxiv.arxiv_services.ListRecordOAI import ListRecordOAI
from flask_api_crawler_arxiv.app_config_dict import app_config
from flask_api_crawler_arxiv.utils.setup_logging import setup_logging


def cron_inject_data_mongodb(app_config, arxset=None):
    """
    Retrieves data from the ArXiv API, converts it, and inserts it into MongoDB.

    Args:
        app_config (dict): Application configuration.
        arxset (str, optional): ARXSET parameter. Defaults to None.
    """

    setup_logging()
    logger = logging.getLogger(__name__)

    # Change ARXSET dynamically
    if arxset is not None:
        app_config["ARXSET"] = arxset

    logger.info("### Creating SERVICES ###")
    arxiv_list_record_service = ListRecordOAI(app_config)
    arxiv_record_converter_service = RecordConverterOAI()

    logger.info("Retrieving all data from arXiv")
    xml_string_of_today_from_arxiv = arxiv_list_record_service.get_record(date.today())

    logger.info("Converting XML string into dictionary")
    dict_of_today_from_arxiv = arxiv_record_converter_service.get_listrecord_dict(
        xml_string_of_today_from_arxiv
    )

    # Connection string is a tad different than usual simply because the name of the service mongodb is mongodb so no localhost here
    manager = MongoDBManager(
        f'mongodb://{app_config["MONGO_INITDB_ROOT_USERNAME"]}:{app_config["MONGO_INITDB_ROOT_PASSWORD"]}@{app_config["MONGO_CONTAINER_NAME"]}:{app_config["MONGO_DOCKER_PORT"]}',
        f'{app_config["MONGO_INITDB_DATABASE"]}',
    )

    logger.info("Attempting OPEN MongoDB connection")
    manager.open_connection()
    logger.info("MongoDB OPEN connection successful")

    manager.perform_transaction(
        lambda db: db.arxiv_data_doc.insert_many(dict_of_today_from_arxiv)
    )
    logger.info("MongoDB TRANSACTION successful")

    logger.info("Attempting CLOSED MongoDB connection")
    manager.close_connection()
    logger.info("MongoDB CLOSED connection successful")


if __name__ == "__main__":
    cron_inject_data_mongodb(app_config)
