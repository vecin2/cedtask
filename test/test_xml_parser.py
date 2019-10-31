import lxml.etree as ET
from core.objects import SourceObjectParser


def test_parse_cdata(fs):
    parser = ET.XMLParser(strip_cdata=False)
    tree = ET.parse("test/processExamples/MeterUsageHistory.xml", parser)
    tree.write("test/processExamples/MessageUsageHistory1.xml")

def test_other():
    parser = ET.XMLParser(strip_cdata=False)
    root = ET.XML('<root><![CDATA[test]]></root>', parser)
    assert "test" == root.text

def test_simple_file():
    #parser = ET.XMLParser(strip_cdata=False)
    source="test/processExamples/SimpleValidationMessageDialogCopy.xml"
    #tree = ET.parse(source, parser)
    #target ="test/processExamples/SimpleValidationMessageDialog1.xml"
    #tree.getroot().text = ET.CDATA('"This is a string"')
    #content = ET.tostring(tree.getroot(),encoding='unicode')
    package_entry =SourceObjectParser().parse(source)
    package_entry.save()
    #assert '"This is a string"' == tree.getroot().text
    #with open(target,"w") as f:
    #    f.write(content)
