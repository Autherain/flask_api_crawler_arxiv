import pytest

from datetime import datetime

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
        xml_source = """<OAI-PMH xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
<responseDate>2024-01-29T16:07:33Z</responseDate>
<request verb="ListRecords" from="2023-11-08" metadataPrefix="oai_dc" set="cs">http://export.arxiv.org/oai2</request>
<ListRecords>
<record>
<header>
<identifier>oai:arXiv.org:0802.3300</identifier>
<datestamp>2024-01-18</datestamp>
<setSpec>cs</setSpec>
</header>
<metadata>
<oai_dc:dc xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
<dc:title>Projective Expected Utility</dc:title>
<dc:creator>La Mura, Pierfrancesco</dc:creator>
<dc:subject>Quantum Physics</dc:subject>
<dc:subject>
Computer Science - Computer Science and Game Theory
</dc:subject>
<dc:subject>Economics - Theoretical Economics</dc:subject>
<dc:description>
Motivated by several classic decision-theoretic paradoxes, and by analogies with the paradoxes which in physics motivated the development of quantum mechanics, we introduce a projective generalization of expected utility along the lines of the quantum-mechanical generalization of probability theory. The resulting decision theory accommodates the dominant paradoxes, while retaining significant simplicity and tractability. In particular, every finite game within this larger class of preferences still has an equilibrium.
</dc:description>
<dc:description>
Comment: 7 pages, to appear in the Proceedings of Quantum Interaction 2008
</dc:description>
<dc:date>2008-02-22</dc:date>
<dc:type>text</dc:type>
<dc:identifier>http://arxiv.org/abs/0802.3300</dc:identifier>
<dc:identifier>J. of Math. Psychology, 53:5 (2009)</dc:identifier>
<dc:identifier>doi:10.1016/j.jmp.2009.02.001</dc:identifier>
</oai_dc:dc>
</metadata>
</record>
<record>
<header>
<identifier>oai:arXiv.org:0803.0966</identifier>
<datestamp>2024-01-01</datestamp>
<setSpec>cs</setSpec>
</header>
<metadata>
<oai_dc:dc xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd">
<dc:title>
New probabilistic interest measures for association rules
</dc:title>
<dc:creator>Hahsler, Michael</dc:creator>
<dc:creator>Hornik, Kurt</dc:creator>
<dc:subject>Computer Science - Databases</dc:subject>
<dc:subject>Statistics - Machine Learning</dc:subject>
<dc:description>
Mining association rules is an important technique for discovering meaningful patterns in transaction databases. Many different measures of interestingness have been proposed for association rules. However, these measures fail to take the probabilistic properties of the mined data into account. In this paper, we start with presenting a simple probabilistic framework for transaction data which can be used to simulate transaction data when no associations are present. We use such data and a real-world database from a grocery outlet to explore the behavior of confidence and lift, two popular interest measures used for rule mining. The results show that confidence is systematically influenced by the frequency of the items in the left hand side of rules and that lift performs poorly to filter random noise in transaction data. Based on the probabilistic framework we develop two new interest measures, hyper-lift and hyper-confidence, which can be used to filter or order mined association rules. The new measures show significantly better performance than lift for applications where spurious rules are problematic.
</dc:description>
<dc:date>2008-03-06</dc:date>
<dc:type>text</dc:type>
<dc:identifier>http://arxiv.org/abs/0803.0966</dc:identifier>
<dc:identifier>Intelligent Data Analysis, 11(5):437-455, 2007</dc:identifier>
<dc:identifier>doi:10.3233/IDA-2007-11502</dc:identifier>
</oai_dc:dc>
</metadata>
</record>
 </ListRecords>
</OAI-PMH>
        """
        result = self.record_converter.get_listrecord_dict(xml_source)
        assert isinstance(result, list)
        # assert 1 == 0
        assert result == [
            {
                "header": {
                    "identifier": "oai:arXiv.org:0802.3300",
                    # "datestamp": "2024-01-18",
                    "datestamp": datetime(2024, 1, 18),
                    "setSpec": "cs",
                },
                "metadata": {
                    "oai_dc:dc": {
                        "@xsi:schemaLocation": "http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd",
                        "dc:title": "Projective Expected Utility",
                        "dc:creator": "La Mura, Pierfrancesco",
                        "dc:subject": [
                            "Quantum Physics",
                            "Computer Science - Computer Science and Game Theory",
                            "Economics - Theoretical Economics",
                        ],
                        "dc:description": [
                            "Motivated by several classic decision-theoretic paradoxes, and by analogies with the paradoxes which in physics motivated the development of quantum mechanics, we introduce a projective generalization of expected utility along the lines of the quantum-mechanical generalization of probability theory. The resulting decision theory accommodates the dominant paradoxes, while retaining significant simplicity and tractability. In particular, every finite game within this larger class of preferences still has an equilibrium.",
                            "Comment: 7 pages, to appear in the Proceedings of Quantum Interaction 2008",
                        ],
                        "dc:date": "2008-02-22",
                        "dc:type": "text",
                        "dc:identifier": [
                            "http://arxiv.org/abs/0802.3300",
                            "J. of Math. Psychology, 53:5 (2009)",
                            "doi:10.1016/j.jmp.2009.02.001",
                        ],
                    }
                },
            },
            {
                "header": {
                    "identifier": "oai:arXiv.org:0803.0966",
                    # "datestamp": "2024-01-01",
                    "datestamp": datetime(2024, 1, 1),
                    "setSpec": "cs",
                },
                "metadata": {
                    "oai_dc:dc": {
                        "@xsi:schemaLocation": "http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd",
                        "dc:title": "New probabilistic interest measures for association rules",
                        "dc:creator": ["Hahsler, Michael", "Hornik, Kurt"],
                        "dc:subject": [
                            "Computer Science - Databases",
                            "Statistics - Machine Learning",
                        ],
                        "dc:description": "Mining association rules is an important technique for discovering meaningful patterns in transaction databases. Many different measures of interestingness have been proposed for association rules. However, these measures fail to take the probabilistic properties of the mined data into account. In this paper, we start with presenting a simple probabilistic framework for transaction data which can be used to simulate transaction data when no associations are present. We use such data and a real-world database from a grocery outlet to explore the behavior of confidence and lift, two popular interest measures used for rule mining. The results show that confidence is systematically influenced by the frequency of the items in the left hand side of rules and that lift performs poorly to filter random noise in transaction data. Based on the probabilistic framework we develop two new interest measures, hyper-lift and hyper-confidence, which can be used to filter or order mined association rules. The new measures show significantly better performance than lift for applications where spurious rules are problematic.",
                        "dc:date": "2008-03-06",
                        "dc:type": "text",
                        "dc:identifier": [
                            "http://arxiv.org/abs/0803.0966",
                            "Intelligent Data Analysis, 11(5):437-455, 2007",
                            "doi:10.3233/IDA-2007-11502",
                        ],
                    }
                },
            },
        ]

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
