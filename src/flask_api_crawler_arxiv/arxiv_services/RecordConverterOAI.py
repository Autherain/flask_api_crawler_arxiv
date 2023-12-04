import xmltodict
import logging


class RecordConverterOAI:
    def __init__(self) -> None:
        """
        Initializes the RecordConverterOAI class.

        This class is designed to convert XML data from OAI-PMH responses to dictionaries.
        """
        self._logger = logging.Logger(__name__)

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
        return listrecord_dict["OAI-PMH"]["ListRecords"]["record"]
