import xmltodict
import logging

from datetime import datetime

from flask_api_crawler_arxiv.utils.setup_logging import setup_logging


class RecordConverterOAI:
    def __init__(self) -> None:
        """
        Initializes the RecordConverterOAI class.

        This class is designed to convert XML data from OAI-PMH responses to dictionaries.
        """
        setup_logging()

        self._logger = logging.getLogger(__name__)

    def xmltodict(self, xml_input: str) -> [dict]:
        """
        Converts XML input to a dictionary using xmltodict.

        Args:
            xml_input (str): XML input string.

        Returns:
            [dict]: List containing the resulting dictionary.
        """
        try:
            xml_dict = xmltodict.parse(xml_input)
        except Exception as e:
            self._logger.warning("xmltodict error occurred during XML parsing: %s", e)
            raise RuntimeError() from e

        if "error" in xml_dict["OAI-PMH"]:
            self._logger.warning(
                "xmltodict error occurred during XML parsing: %s",
                xml_dict["OAI-PMH"]["error"],
            )
            raise RuntimeError(
                "Problem occurred from within the query: %s",
                xml_dict["OAI-PMH"]["error"],
            )

        return xml_dict

    def get_listrecord_dict(self, xml_source: str) -> [dict]:
        """
        Retrieves a list of records as a dictionary from the given XML source.

        Args:
            xml_source (str): XML source string.

        Returns:
            [dict]: List containing the resulting dictionary.
        """
        listrecord_dict = self.xmltodict(xml_source)

        records = (
            listrecord_dict.get("OAI-PMH", {}).get("ListRecords", {}).get("record", [])
        )

        converted_records = []
        for item in records:
            try:
                item["header"]["datestamp"] = datetime.strptime(
                    item["header"]["datestamp"], "%Y-%m-%d"
                )
                converted_records.append(item)
            except (KeyError, ValueError) as e:
                self._logger.warning(
                    "Error converting record: %s. Removing the record.", e
                )

        return converted_records
