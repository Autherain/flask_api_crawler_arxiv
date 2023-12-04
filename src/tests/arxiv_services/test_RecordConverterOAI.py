import pytest

from flask_api_crawler_arxiv.arxiv_services.RecordConverterOAI import RecordConverterOAI


class TestRecordConverterOAI:
    @classmethod
    def setup_class(cls):
        # Setup class-level resources or fixtures
        cls.record_converter = RecordConverterOAI()

    @classmethod
    def teardown_class(cls):
        # Teardown class-level resources or fixtures
        pass

    def setup_method(self):
        # Setup method-level resources or fixtures
        pass

    def teardown_method(self):
        # Teardown method-level resources or fixtures
        pass

    def test_initialization(self):
        # Test that the RecordConverterOAI instance is created successfully
        assert isinstance(self.record_converter, RecordConverterOAI)

    def test_xmltodict(self):
        # Test the xmltodict method with valid XML input
        xml_input = """<?xml version="1.0" encoding="UTF-8"?>
            <OAI-PMH>
                <error>Error message</error>
            </OAI-PMH>
        """
        # Disable broad-except to catch all exceptions during testing.
        # pylint: disable=broad-except
        with pytest.raises(RuntimeError):
            self.record_converter.xmltodict(xml_input)

    def test_get_listrecord_dict(self):
        # Test the get_listrecord_dict method with valid XML input
        xml_source = """<?xml version="1.0" encoding="UTF-8"?>
            <OAI-PMH>
                <ListRecords>
                    <record>Record 1</record>
                    <record>Record 2</record>
                </ListRecords>
            </OAI-PMH>
        """
        result = self.record_converter.get_listrecord_dict(xml_source)
        assert isinstance(result, list)
        assert result == ["Record 1", "Record 2"]

    def test_get_listrecord_dict_with_error(self):
        # Test the get_listrecord_dict method with XML containing an error
        xml_source = """<?xml version="1.0" encoding="UTF-8"?>
            <OAI-PMH>
                <error>Error message</error>
            </OAI-PMH>
        """
        # Disable broad-except to catch all exceptions during testing.
        # pylint: disable=broad-except
        with pytest.raises(RuntimeError):
            self.record_converter.get_listrecord_dict(xml_source)
