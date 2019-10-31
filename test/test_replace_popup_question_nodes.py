from collections import defaultdict
import os
from shutil import copyfile,rmtree

import pytest


from test.utils.fake_logging import FakeLogger
from core.objects import PackageEntry,SourceObjectParser
from use_cases.popup_replacer import PopupReplacer

no_process_found_msg="No processes found containing PopupQuestions"

@pytest.fixture()
def cleandir():
    try:
        script_dir =os.path.dirname(__file__)
        #rmtree(script_dir+"/tmp")
    except OSError:
        pass

def full_path(relative_path):
    script_dir =os.path.dirname(__file__)
    original_file = script_dir+"/"+relative_path
    target = script_dir +"/tmp/test_processes/"+ relative_path
    os.makedirs(os.path.dirname(target), exist_ok=True)
    copyfile(original_file,target)
    return target


def add_real_file(fs, relative_path, fake_path=None):
    real_path =full_path(relative_path.replace("/",str(os.sep)))
    fs.add_real_file(real_path,False,fake_path)

logical_process="processExamples/SimpleValidationMessageDialog.xml"
validation_process="processExamples/SimpleValidationQuestionPopup.xml"

def replace(logger,filesystem_path=None,file_with_paths=None):
    popup_replacer = PopupReplacer(logger)
    popup_replacer.replace(filesystem_path,file_with_paths=file_with_paths)

@pytest.mark.usefixtures("cleandir")
def test_nothing_found():
    logger = FakeLogger()
    replace(logger,"/pc/config")
    assert "INFO "+no_process_found_msg== logger.lines[1]

@pytest.mark.usefixtures("cleandir")
def test_ignore_processes_without_popup_nodes():
    logger = FakeLogger()
    target =full_path("processExamples/EmptyProcess.xml")
    replace(logger,target)
    assert "INFO "+no_process_found_msg== logger.lines[1]


@pytest.mark.usefixtures("cleandir")
def test_replaces_one_popup():
    logger = FakeLogger()
    source=full_path(validation_process)
    package_entry = SourceObjectParser().parse(source)
    assert  package_entry.process_definition.find("PopupQuestionNode") is not None
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
    assert message_dialog_node is not None
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
    text='"The search criteria retrieved no Customers"'
    assert text==\
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


@pytest.mark.usefixtures("cleandir")
def test_replaces_multiple_popups():
    logger = FakeLogger()
    source=full_path("processExamples/MultiplePopups.xml")
    package_entry = SourceObjectParser().parse(source)
    assert  2 ==len(list(package_entry.process_definition.findall("PopupQuestionNode")))

    replace(logger,os.path.dirname(source))
    assert "INFO Replacing 2 popup(s) for '"+source+"'"== logger.lines[1]
    assert "INFO 1 Processes found containing PopupQuestions"== logger.lines[2]
    package_entry = SourceObjectParser().parse(source)
    assert "FrameworkCommon.API.PopUpQuestion.MessageDialog" in package_entry.imports()
    assert  None == package_entry.process_definition.find("PopupQuestionNode")
    assert 1 == len(package_entry.process_definition.findall("ThisNode"))

@pytest.mark.usefixtures("cleandir")
def test_replace_inner_process():
    logger = FakeLogger()
    source=full_path("processExamples/MainProcess/ValidationProcess/SubValidationProcess.xml")
    parent=full_path("processExamples/MainProcess/ValidationProcess.xml")
    main=full_path("processExamples/MainProcess.xml")
    process_definition = SourceObjectParser().parse(source)
    assert  process_definition.root.find("PopupQuestionNode") is not None

    replace(logger,os.path.dirname(source))
    process_definition = SourceObjectParser().parse(source)
    assert  None == process_definition.root.find("PopupQuestionNode")
    main_process = SourceObjectParser().parse(main)
    assert "FrameworkCommon.API.PopUpQuestion.MessageDialog" in main_process.imports()
    assert "INFO 1 Processes found containing PopupQuestions"== logger.lines[2]


@pytest.mark.usefixtures("cleandir")
def test_replace_error_popup():
    logger = FakeLogger()
    source=full_path("processExamples/SimpleValidationErrorQuestionPopup.xml")
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

@pytest.mark.usefixtures("cleandir")
def test_replace_formProcess_popup():
    logger = FakeLogger()
    source=full_path("processExamples/FormProcessQuestionPopup.xml")
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


@pytest.mark.usefixtures("cleandir")
def test_replace_formProcess_popup():
    logger = FakeLogger()
    source=full_path("processExamples/MainProcess/ValidationFormProcess.xml")
    main=full_path("processExamples/MainProcess.xml")

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

@pytest.mark.usefixtures("cleandir")
def test_read_fromfile_popup():
    logger = FakeLogger()
    source=full_path("processExamples/SimpleValidationQuestionPopup.xml")
    script_dir =os.path.dirname(__file__)
    paths_file=script_dir+"/tmp/my_paths.txt"
    with open(paths_file,'w') as f:
            f.write(source)

    package_entry = SourceObjectParser().parse(source)

    replace(logger,file_with_paths=paths_file)
    message="Replacing 1 popup(s) for '/home/dgarcia/dev/python/cedtask/test/tmp/test_processes/processExamples/SimpleValidationQuestionPopup.xml'"
    assert "INFO "+message == logger.lines[1]
    package_entry = SourceObjectParser().parse(source)
    data_flow = package_entry.process_definition.find("DataFlow")
    assert "fieldStore0" == data_flow.find("FromNode").get("name")
