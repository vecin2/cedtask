from collections import defaultdict
import pytest
import os

from test.utils.fake_logging import FakeLogger
from core.objects import PackageEntry,SourceObjectParser
from use_cases.popup_replacer import PopupReplacer

no_process_found_msg="No processes found containing PopupQuestions"


def full_path(relative_path):
    script_dir =os.path.dirname(__file__)
    return script_dir+"/"+relative_path

def add_real_file(fs, relative_path, fake_path=None):
    real_path =full_path(relative_path.replace("/",str(os.sep)))
    fs.add_real_file(real_path,False,fake_path)

logical_process="processExamples/SimpleValidationMessageDialog.xml"
validation_process="processExamples/SimpleValidationQuestionPopup.xml"

def replace(logger,filesystem_path=None,file_with_paths=None):
    popup_replacer = PopupReplacer(logger)
    popup_replacer.replace(filesystem_path,file_with_paths=file_with_paths)

def test_nothing_found():
    logger = FakeLogger()
    replace(logger,"/pc/config")
    assert "INFO "+no_process_found_msg== logger.lines[1]

def test_ignore_processes_without_popup_nodes(fs):
    logger = FakeLogger()
    add_real_file(fs,
                  logical_process,
                  "/repo")
    replace(logger,"/repo")
    assert "INFO "+no_process_found_msg== logger.lines[1]


def test_replaces_one_popup(fs):
    logger = FakeLogger()
    source=full_path(validation_process)
    fs.add_real_file(source,read_only=False)
    package_entry = SourceObjectParser().parse(source)
    assert  package_entry.process_definition.find("PopupQuestionNode")
    assert  "noCustomersFound" ==package_entry.process_definition.find("PopupQuestionNode").get("name")
    assert  "198" ==package_entry.process_definition.find("PopupQuestionNode").get("x")
    assert  "48" ==package_entry.process_definition.find("PopupQuestionNode").get("y")

    replace(logger,os.path.dirname(source))
    assert "INFO 1 Processes found containing PopupQuestions"== logger.lines[2]
    assert "INFO Replacing 1 popup(s) for '"+source+"'"== logger.lines[1]
    package_entry = SourceObjectParser().parse(source)
    assert "FrameworkCommon.API.PopUpQuestion.MessageDialog" in package_entry.imports()
    assert  None == package_entry.process_definition.find("PopupQuestionNode")
    message_dialog_node=  package_entry.process_definition.find("ChildProcess") 
    assert message_dialog_node
    assert "MessageDialog" == message_dialog_node.find("ProcessDefinitionReference").get("name")
    assert "fieldStore0" == package_entry.process_definition.find("ThisNode").get("name")
    assert "148" == package_entry.process_definition.find("ThisNode").get("x")
    assert "128" == package_entry.process_definition.find("ThisNode").get("y")
    data_flow = package_entry.process_definition.find("DataFlow")
    assert "fieldStore0" == data_flow.find("FromNode").get("name")
    assert "noCustomersFound" == data_flow.find("ToNode").get("name")
    data_flow_entries=data_flow.findall("DataFlowEntry")
    line1_from = data_flow_entries[0].find("FromField")
    parameter_assigment =line1_from.find("ParameterAssignment")
    assert "0" == parameter_assigment.get("exceptionStrategy")
    assert "EcmaScript" == parameter_assigment.get("language")
    assert "" == parameter_assigment.get("name")
    assert "" == parameter_assigment.get("version")
    verbatim =parameter_assigment.find("Verbatim")
    assert "text" == verbatim.get("fieldName")
    assert '"The search criteria retrieved no Customers"' ==\
            verbatim.text.strip()
    message_type = data_flow_entries[1].find("FromField")
    parameter_assigment =message_type.find("ParameterAssignment")
    assert "0" == parameter_assigment.get("exceptionStrategy")
    assert "EcmaScript" == parameter_assigment.get("language")
    assert "" == parameter_assigment.get("name")
    assert "" == parameter_assigment.get("version")
    verbatim =parameter_assigment.find("Verbatim")
    assert "text" == verbatim.get("fieldName")
    assert 'MessageDialog.INFORMATION_TYPE' ==\
            verbatim.text.strip()

    line1 = data_flow.find("DataFlowEntry").find("ToField")
    assert "line1" == line1.find("FieldDefinitionReference").get("name")
    assert "The search criteria retrieved no Customers"
    graph_node_list=data_flow.find("GraphNodeList")
    assert "" == graph_node_list.get("name")
    graph_node =graph_node_list.find("GraphNode")
    assert "" == graph_node.get("icon")
    assert "true" == graph_node.get("isLabelHolder")
    assert "" == graph_node.get("label")
    assert "" == graph_node.get("name")
    assert "198" == graph_node.get("x")
    assert "128" == graph_node.get("y")


def test_replaces_multiple_popups(fs):
    logger = FakeLogger()
    source=full_path("processExamples/MultiplePopups.xml")
    fs.add_real_file(source,read_only=False)
    package_entry = SourceObjectParser().parse(source)
    assert  2 ==len(list(package_entry.process_definition.findall("PopupQuestionNode")))

    replace(logger,os.path.dirname(source))
    assert "INFO Replacing 2 popup(s) for '"+source+"'"== logger.lines[1]
    assert "INFO 1 Processes found containing PopupQuestions"== logger.lines[2]
    package_entry = SourceObjectParser().parse(source)
    assert "FrameworkCommon.API.PopUpQuestion.MessageDialog" in package_entry.imports()
    assert  None == package_entry.process_definition.find("PopupQuestionNode")
    assert 1 == len(package_entry.process_definition.findall("ThisNode"))

def test_replace_inner_process(fs):
    logger = FakeLogger()
    source=full_path("processExamples/MainProcess/ValidationProcess/SubValidationProcess.xml")
    fs.add_real_file(source,read_only=False)
    parent=full_path("processExamples/MainProcess/ValidationProcess.xml")
    fs.add_real_file(parent,read_only=False)

    main=full_path("processExamples/MainProcess.xml")
    fs.add_real_file(main,read_only=False)
    process_definition = SourceObjectParser().parse(source)
    assert  process_definition.root.find("PopupQuestionNode")

    replace(logger,os.path.dirname(source))
    process_definition = SourceObjectParser().parse(source)
    assert  None == process_definition.root.find("PopupQuestionNode")
    main_process = SourceObjectParser().parse(main)
    assert "FrameworkCommon.API.PopUpQuestion.MessageDialog" in main_process.imports()
    assert "INFO 1 Processes found containing PopupQuestions"== logger.lines[2]


@pytest.mark.skip 
def test_replace_inner_process_with_main_FormProcess(fs):
    logger = FakeLogger()
    source=full_path("processExamples/MainFormProcess/ValidationProcess.xml")
    fs.add_real_file(source,read_only=False)
    main=full_path("processExamples/MainProcess/ValidationProcess.xml")
    fs.add_real_file(main,read_only=False)

    process_definition = SourceObjectParser().parse(source)
    assert  process_definition.root.find("PopupQuestionNode")

    replace(logger,os.path.dirname(source))
    #process_definition = SourceObjectParser().parse(source)
    #assert  None == process_definition.root.find("PopupQuestionNode")
    #main_process = SourceObjectParser().parse(main)
    #assert "FrameworkCommon.API.PopUpQuestion.MessageDialog" in main_process.imports()
    #assert "INFO 1 Processes found containing PopupQuestions"== logger.lines[2]


def test_replace_error_popup(fs):
    logger = FakeLogger()
    source=full_path("processExamples/SimpleValidationErrorQuestionPopup.xml")
    fs.add_real_file(source,read_only=False)
    package_entry = SourceObjectParser().parse(source)
    popupquestion =  package_entry.process_definition.find("PopupQuestionNode")
    assert "Error" == popupquestion.get("question")

    replace(logger,os.path.dirname(source))

    package_entry = SourceObjectParser().parse(source)
    data_flow = package_entry.process_definition.find("DataFlow")
    assert "fieldStore0" == data_flow.find("FromNode").get("name")
    assert "noCustomersFound" == data_flow.find("ToNode").get("name")
    data_flow_entries=data_flow.findall("DataFlowEntry")
    line1_from = data_flow_entries[0].find("FromField")
    parameter_assigment =line1_from.find("ParameterAssignment")
    assert "0" == parameter_assigment.get("exceptionStrategy")
    assert "EcmaScript" == parameter_assigment.get("language")
    assert "" == parameter_assigment.get("name")
    assert "" == parameter_assigment.get("version")
    verbatim =parameter_assigment.find("Verbatim")
    assert "text" == verbatim.get("fieldName")
    assert '"The search criteria retrieved no Customers"' ==\
            verbatim.text.strip()
    message_type = data_flow_entries[1].find("FromField")
    parameter_assigment =message_type.find("ParameterAssignment")
    assert "0" == parameter_assigment.get("exceptionStrategy")
    assert "EcmaScript" == parameter_assigment.get("language")
    assert "" == parameter_assigment.get("name")
    assert "" == parameter_assigment.get("version")
    verbatim =parameter_assigment.find("Verbatim")
    assert "text" == verbatim.get("fieldName")
    assert 'MessageDialog.ERROR_TYPE' ==\
            verbatim.text.strip()

def test_replace_formProcess_popup(fs):
    logger = FakeLogger()
    source=full_path("processExamples/FormProcessQuestionPopup.xml")
    fs.add_real_file(source,read_only=False)
    package_entry = SourceObjectParser().parse(source)
    popupquestion =  package_entry.process_definition.find("PopupQuestionNode")
    assert "Error" == popupquestion.get("question")
    replace(logger,os.path.dirname(source))

    package_entry = SourceObjectParser().parse(source)
    data_flow = package_entry.process_definition.find("DataFlow")
    assert "fieldStore0" == data_flow.find("FromNode").get("name")
    assert "invalidUsername" == data_flow.find("ToNode").get("name")
    data_flow_entries=data_flow.findall("DataFlowEntry")
    line1_from = data_flow_entries[0].find("FromField")
    parameter_assigment =line1_from.find("ParameterAssignment")
    assert "0" == parameter_assigment.get("exceptionStrategy")
    assert "EcmaScript" == parameter_assigment.get("language")
    assert "" == parameter_assigment.get("name")
    assert "" == parameter_assigment.get("version")
    verbatim =parameter_assigment.find("Verbatim")
    assert "text" == verbatim.get("fieldName")
    assert '"The usename is not valid"' ==\
            verbatim.text.strip()
    message_type = data_flow_entries[1].find("FromField")
    parameter_assigment =message_type.find("ParameterAssignment")
    assert "0" == parameter_assigment.get("exceptionStrategy")
    assert "EcmaScript" == parameter_assigment.get("language")
    assert "" == parameter_assigment.get("name")
    assert "" == parameter_assigment.get("version")
    verbatim =parameter_assigment.find("Verbatim")
    assert "text" == verbatim.get("fieldName")
    assert 'MessageDialog.ERROR_TYPE' ==\
            verbatim.text.strip()


def test_replace_formProcess_popup(fs):
    logger = FakeLogger()
    source=full_path("processExamples/MainProcess/ValidationFormProcess.xml")
    fs.add_real_file(source,read_only=False)
    main=full_path("processExamples/MainProcess.xml")
    fs.add_real_file(main,read_only=False)

    form_process = SourceObjectParser().parse(source)
    popupquestion =  form_process.process_definition.find("PopupQuestionNode")
    assert "Error" == popupquestion.get("question")

    replace(logger,os.path.dirname(source))

    package_entry = SourceObjectParser().parse(source)
    data_flow = package_entry.process_definition.find("DataFlow")
    assert "fieldStore0" == data_flow.find("FromNode").get("name")
    assert "invalidPassword" == data_flow.find("ToNode").get("name")
    data_flow_entries=data_flow.findall("DataFlowEntry")
    line1_from = data_flow_entries[0].find("FromField")
    parameter_assigment =line1_from.find("ParameterAssignment")
    assert "0" == parameter_assigment.get("exceptionStrategy")
    assert "EcmaScript" == parameter_assigment.get("language")
    assert "" == parameter_assigment.get("name")
    assert "" == parameter_assigment.get("version")
    verbatim =parameter_assigment.find("Verbatim")
    assert "text" == verbatim.get("fieldName")
    assert '"Please make sure you password is correct"' ==\
            verbatim.text.strip()
    message_type = data_flow_entries[1].find("FromField")
    parameter_assigment =message_type.find("ParameterAssignment")
    assert "0" == parameter_assigment.get("exceptionStrategy")
    assert "EcmaScript" == parameter_assigment.get("language")
    assert "" == parameter_assigment.get("name")
    assert "" == parameter_assigment.get("version")
    verbatim =parameter_assigment.find("Verbatim")
    assert "text" == verbatim.get("fieldName")
    assert 'MessageDialog.ERROR_TYPE' ==\
            verbatim.text.strip()

def test_read_fromfile_popup(fs):
    logger = FakeLogger()
    source=full_path("processExamples/SimpleValidationQuestionPopup.xml")
    fs.add_real_file(source,read_only=False)
    fs.create_file("paths.txt",contents=source+"\n")

    package_entry = SourceObjectParser().parse(source)

    replace(logger,file_with_paths="paths.txt")
    message="Replacing 1 popup(s) for '/home/dgarcia/dev/python/cedtask/test/processExamples/SimpleValidationQuestionPopup.xml'"
    assert "INFO "+message == logger.lines[1]
    package_entry = SourceObjectParser().parse(source)
    data_flow = package_entry.process_definition.find("DataFlow")
    assert "fieldStore0" == data_flow.find("FromNode").get("name")
