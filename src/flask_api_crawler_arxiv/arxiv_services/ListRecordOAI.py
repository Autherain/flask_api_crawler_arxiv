from pydantic import BaseModel, Field, ValidationError
import logging
import datetime
import requests

from flask_api_crawler_arxiv.utils.setup_logging import setup_logging


class _ListRecordOAIParametersInit(BaseModel):
    """
    Pydantic BaseModel for initializing parameters for ListRecordOAI.

    Attributes:
    - host (str): ARXHOST, the host URL for the ARxiv API.
    - set (str): ARXSET, the set identifier for the ARxiv API.
    - check_time (int): ARXCHECKTIMEMINUTES, the check time interval in minutes.
    - time_out (int): ARXTIMEOUT, the timeout duration for API requests.
    """

    host: str = Field(min_length=1, max_length=65, alias="ARXHOST")
    set: str = Field(min_length=1, max_length=65, alias="ARXSET")
    check_time: int = Field(gt=0, alias="ARXCHECKTIMEMINUTES")
    time_out: int = Field(gt=0, alias="ARXTIMEOUT")


class _ListRecordParametersQuery(BaseModel):
    """
    Pydantic BaseModel for building query parameters for listing records.

    Attributes:
    - metadataPrefix (str): The metadata prefix for records (default: "oai_dc").
    - verb (str): The OAI-PMH verb for the request (default: "ListRecords").
    - set (str): The set identifier for the request.
    - until (datetime.date): The date until which records should be fetched.
    """

    metadataPrefix: str = Field(default="oai_dc")
    verb: str = Field(default="ListRecords")
    set: str = Field(min_length=1, max_length=32)
    until: datetime.date


class ListRecordOAI:
    """
    ListRecordOAI is a class for fetching records from the ARxiv API using OAI-PMH protocol.

    Parameters:
    - app_config_dict (dict): Dictionary containing configuration parameters for initializing the class.

    Methods:
    - __init__(self, app_config_dict: dict) -> None:
        Initializes the ListRecordOAI instance with the provided configuration dictionary.

    - get_record(self, until_date: datetime.date(2000, 1, 1)) -> str:
        Fetches records from the ARxiv API until the specified date.

        Parameters:
        - until_date (datetime.date): The date until which records should be fetched.

        Returns:
        - str: Retrieved records in string format.

    Private Methods:
    - _build_parameters_query(self, until_date: datetime.date) -> _ListRecordParametersQuery:
        Builds the query parameters for listing records based on the provided until_date.

        Parameters:
        - until_date (datetime.date): The date until which records should be fetched.

        Returns:
        - _ListRecordParametersQuery: Query parameters for listing records.

    - _list_record(self, parameters_query: _ListRecordParametersQuery) -> str:
        Sends a request to the ARxiv API with the specified query parameters and retrieves records.

        Parameters:
        - parameters_query (_ListRecordParametersQuery): Query parameters for listing records.

        Returns:
        - str: Retrieved records in string format.
    """

    def __init__(self, app_config_dict: dict) -> None:
        """
        Initializes a ListRecordOAI instance with the provided configuration dictionary.

        Parameters:
        - app_config_dict (dict): Dictionary containing configuration parameters.
        """

        setup_logging()

        self._logger = logging.getLogger(__name__)

        try:
            self._parameters = _ListRecordOAIParametersInit(**app_config_dict)
            self._logger.info("Config dictionnary successfully loaded")
        except ValidationError as e:
            self._logger.fatal("RecordFetcher was not able to be initialized :%s", e)
            raise ValidationError() from e

    def _build_parameters_query(
        self, until_date: datetime.date
    ) -> _ListRecordParametersQuery:
        """
        Builds the query parameters for listing records based on the provided until_date.

        Parameters:
        - until_date (datetime.date): The date until which records should be fetched.

        Returns:
        - _ListRecordParametersQuery: Query parameters for listing records.
        """
        try:
            return _ListRecordParametersQuery(
                **{
                    "set": self._parameters.set,
                    "until": until_date,
                }
            )
        except Exception as e:
            self._logger.warning("Error occurred when building query parameter: %s", e)
            raise RuntimeError() from e

    def _list_record(self, parameters_query: _ListRecordParametersQuery) -> str:
        """
        Sends a request to the ARxiv API with the specified query parameters and retrieves records.

        Parameters:
        - parameters_query (_ListRecordParametersQuery): Query parameters for listing records.

        Returns:
        - str: Retrieved records in string format.
        """
        query_parameter_dict = parameters_query.model_dump(by_alias=True)

        try:
            response = requests.get(
                url=self._parameters.host,
                params=query_parameter_dict,
                timeout=self._parameters.time_out,
            )

            if response.status_code != 200:
                error_text = f"An error occurred when interacting with ARxiv API: {response.status_code}"
                self._logger.warning(error_text)
                raise ValueError(error_text)

            return response.text

        except Exception as e:
            self._logger.warning("Unexpected error with API :%s", e)
            raise RuntimeError() from e

    def get_record(self, until_date: datetime.date = None) -> str:
        """
        Fetches records from the ARxiv API until the specified date.

        Parameters:
        - until_date (datetime.date): The date until which records should be fetched. Defaults to None.

        Returns:
        - str: Retrieved records in string format.
        """
        if until_date is None:
            until_date = datetime.date(year=2000, month=1, day=1)

        self._logger.info(f"Date used is {until_date}")
        query_parameter = self._build_parameters_query(until_date)
        return self._list_record(query_parameter)
