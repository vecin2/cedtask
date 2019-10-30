import lxml.etree as ET


def test_parse_cdata(fs):
    parser = ET.XMLParser(strip_cdata=False)
    tree = ET.parse("test/processExamples/MeterUsageHistory.xml", parser)
    tree.write("test/processExamples/MessageUsageHistory1.xml")
