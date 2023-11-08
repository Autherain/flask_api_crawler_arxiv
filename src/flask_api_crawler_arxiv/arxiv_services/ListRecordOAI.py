from pydantic import BaseModel, Field, ValidationError
import logging
import datetime
import requests


class _ListRecordOAIParametersInit(BaseModel):
    host: str = Field(min_length=1, max_length=65, alias="ARXHOST")
    set: str = Field(min_length=1, max_length=65, alias="ARXSET")
    check_time: int = Field(gt=0, alias="ARXCHECKTIMEMINUTES")
    time_out: int = Field(gt=0, alias="ARXTIMEOUT")


class _ListRecordParametersQuery(BaseModel):
    metadataPrefix: str = Field(default="oai_dc")
    verb: str = Field(default="ListRecords")
    set: str = Field(min_length=1, max_length=32)
    until: datetime.date


class ListRecordOAI:
    def __init__(self, app_config_dict: dict) -> None:
        self._logger = logging.Logger(__name__)

        try:
            self._parameters = _ListRecordOAIParametersInit(**app_config_dict)
        except ValidationError as e:
            self._logger.fatal("RecordFetcher was not able to be initialized :%s", e)
            raise ValidationError() from e

    def _build_parameters_query(
        self, until_date: datetime.date
    ) -> _ListRecordParametersQuery:
        try:
            return _ListRecordParametersQuery(
                **{
                    "set": self._parameters.set,
                    "until": until_date,
                }
            )
        except Exception as e:
            self._logger.warning("Error occured when building query parameter: %s", e)
            raise RuntimeError() from e

    def _list_record(self, parameters_query: _ListRecordParametersQuery) -> str:
        query_parameter_dict = parameters_query.model_dump(by_alias=True)

        try:
            response = requests.get(
                url=self._parameters.host,
                params=query_parameter_dict,
                timeout=self._parameters.time_out,
            )

            if response.status_code != 200:
                self._logger.warning(
                    "An error occured when interacting with ARxiv API %s",
                    response.status_code,
                )

            return response.text

        except Exception as e:
            self._logger.warning("Unexpected error with API :%s", e)
            raise RuntimeError() from e

    def get_record(self, until_date: datetime.date(2000, 1, 1)) -> str:
        query_parameter = self._build_parameters_query(until_date)
        return self._list_record(query_parameter)
