import datetime
import pytest
import time

from flask_api_crawler_arxiv.arxiv_services.ListRecordOAI import ListRecordOAI

# Define test data
valid_config = {
    "ARXHOST": "http://export.arxiv.org/oai2",
    "ARXSET": "cs",
    "ARXCHECKTIMEMINUTES": 120,
    "ARXTIMEOUT": 120,
}


class TestListRecordOAI:
    @classmethod
    def setup_class(cls):
        # Setup code that runs once for the entire test class
        cls.list_record = ListRecordOAI(valid_config)

    @classmethod
    def teardown_class(cls):
        # Teardown code that runs once for the entire test class
        pass

    def setup_method(self):
        # Setup code that runs before each test method
        pass

    def teardown_method(self):
        # Teardown code that runs after each test method
        pass

    def test_initialization(self):
        assert isinstance(self.list_record, ListRecordOAI)

    def test_get_record(self):
        until_date = datetime.date(2000, 1, 1)
        result = self.list_record.get_record(until_date)
        assert isinstance(result, str)

    def test_invalid_config(self):
        invalid_config = {
            "ARXHOST": "",  # Invalid empty host
            "ARXSET": "cs",
            "ARXCHECKTIMEMINUTES": -1,  # Invalid negative check_time
            "ARXTIMEOUT": 120,
        }
        with pytest.raises(Exception):
            ListRecordOAI(invalid_config)

    def test_build_parameters_query(self):
        until_date = datetime.date(2000, 1, 1)
        query_parameters = self.list_record._build_parameters_query(until_date)
        assert query_parameters.set == valid_config["ARXSET"]
        assert query_parameters.until == until_date

    def test_list_record(self):
        time.sleep(
            5
        )  # Definetely not the best idea but API block users from querying data every 5s.
        until_date = datetime.date(2000, 1, 1)
        query_parameters = self.list_record._build_parameters_query(until_date)
        result = self.list_record._list_record(query_parameters)
        assert isinstance(result, str)

    def test_list_record_invalid_host(self):
        invalid_config = {
            "ARXHOST": "http://invalid-host",  # Invalid host
            "ARXSET": "cs",
            "ARXCHECKTIMEMINUTES": 120,
            "ARXTIMEOUT": 120,
        }
        list_record = ListRecordOAI(invalid_config)
        until_date = datetime.date(2000, 1, 1)
        with pytest.raises(Exception):
            list_record._list_record(query_parameters)
