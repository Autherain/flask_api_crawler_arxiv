import logging
from flask_api_crawler_arxiv.mongodb.MongodbManager import MongoDBManager
from flask_api_crawler_arxiv.arxiv_services.RecordConverterOAI import RecordConverterOAI
from flask_api_crawler_arxiv.arxiv_services.ListRecordOAI import ListRecordOAI
from flask_api_crawler_arxiv.app_config_dict import app_config
import os
import sys
from datetime import date

# Add the path to the modules directory (going up two levels). It will enable not to meddle with path when invoking this script with cron.
current_script_path = os.path.dirname(os.path.abspath(__file__))
project_root_path = os.path.abspath(
    os.path.join(current_script_path, "..", ".."))
sys.path.append(project_root_path)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
)


def cron_inject_data_mongodb():
    """
    This function retrieves data from the ArXiv API, converts it, and inserts it into MongoDB.
    Function only used with cron and this is why there is an sys.path.append inside the script.
    """
    logging.info("### Creating SERVICES ###")
    arxiv_list_record_service = ListRecordOAI(app_config)
    arxiv_record_converter_service = RecordConverterOAI()

    logging.info("Retrieving all data from arxiv")
    xml_string_of_today_from_arxiv = arxiv_list_record_service.get_record(
        date.today())

    logging.info("Converting XML string into dictionnary")
    dict_of_today_from_arxiv = arxiv_record_converter_service.get_listrecord_dict(
        xml_string_of_today_from_arxiv
    )

    # Connection string is a tad different than usual simply because the name of the service mongodb is mongodb so no localhost here
    manager = MongoDBManager(
        f'mongodb://{app_config["MONGO_INITDB_ROOT_USERNAME"]}:{app_config["MONGO_INITDB_ROOT_PASSWORD"]}@{
            app_config["MONGO_CONTAINER_NAME"]}:{app_config["MONGO_DOCKER_PORT"]}',
        f'{app_config["MONGO_INITDB_DATABASE"]}',
    )

    logging.info("Attempting OPEN MongoDB connection")
    manager.open_connection()
    logging.info("MongoDB OPEN connection successfull")

    manager.perform_transaction(
        lambda db: db.arxiv_data_doc.insert_many(dict_of_today_from_arxiv)
    )
    logging.info("MongoDB TRANSACTION successfull")

    logging.info("Attempting CLOSED MongoDB connection")
    manager.close_connection()
    logging.info("MongoDB CLOSED connection successfull")


if __name__ == "__main__":
    cron_inject_data_mongodb()
