import os
import lxml.etree as ET

from core.objects import PackageEntry,SourceObjectParser


def full_path(relative_path):
    script_dir =os.path.dirname(__file__)
    return script_dir+"/"+relative_path

import1 ="FrameworkCommon.API.PopUpQuestion.MessageDialog"
import2 ="FrameworkCommon.API.PopUpQuestion.MessageDialogTopic"
def test_imports(fs):
    source=full_path("processExamples/SimpleValidationMessageDialog.xml")
    fs.add_real_file(source)
    package_entry = SourceObjectParser().parse(source)
    assert [import1,import2] == package_entry.imports()

def test_add_first_imports(fs):
    source=full_path("processExamples/EmptyProcess.xml")
    fs.add_real_file(source)
    package_entry = SourceObjectParser().parse(source)
    package_entry.add_import(import1)
    package_entry.add_import(import2)
    assert [import2,import1] == package_entry.imports()

def test_add_import_to_existing_imports(fs):
    source=full_path("processExamples/SimpleValidationMessageDialog.xml")
    fs.add_real_file(source)
    package_entry = SourceObjectParser().parse(source)
    import3='FrameworkCommon.API.PopUpQuestion.ConfirmationDialog'
    package_entry.add_import(import3)
    assert [import3,import1,import2] == package_entry.imports()

def test_add_duplicate_import_adds_nothing(fs):
    source=full_path("processExamples/EmptyProcess.xml")
    fs.add_real_file(source)
    package_entry = SourceObjectParser().parse(source)
    import3='FrameworkCommon.API.PopUpQuestion.ConfirmationDialog'
    package_entry.add_import(import3)

    package_entry.add_import(import3)

    assert [import3] == package_entry.imports()

def test_get_package_entry_from_process_definition(fs):
    source=full_path("processExamples/MainProcess/ValidationProcess.xml")
    fs.add_real_file(source)
    outer_filepath=full_path("processExamples/MainProcess.xml")
    fs.add_real_file(outer_filepath)

    validation_process_def= SourceObjectParser().parse(source)
    package_entry = validation_process_def.get_main_process()

    assert outer_filepath == package_entry.filepath

def test_get_package_entry_from_process_definition_recursive(fs):
    source=full_path("processExamples/MainProcess/ValidationProcess/SubValidationProcess.xml")
    fs.add_real_file(source)
    fs.add_real_file(full_path("processExamples/MainProcess/ValidationProcess.xml"))
    main_process=full_path("processExamples/MainProcess.xml")
    fs.add_real_file(main_process)

    validation_process_def= SourceObjectParser().parse(source)
    package_entry = validation_process_def.get_main_process()

    assert main_process == package_entry.filepath

def test_get_package_entry_null_if_not_found(fs):
    source=full_path("processExamples/MainProcess/ValidationProcess/SubValidationProcess.xml")
    fs.add_real_file(source)
    fs.add_real_file(full_path("processExamples/MainProcess/ValidationProcess.xml"))
    #we do not add main

    validation_process_def= SourceObjectParser().parse(source)
    package_entry = validation_process_def.get_main_process()

    assert None == package_entry

def test_package_entry_replace_popupQuestionNode(fs):
    source=full_path("processExamples/SimpleValidationQuestionPopup.xml")
    fs.add_real_file(source)
    package_entry = SourceObjectParser().parse(source)
    popup_question =package_entry.process_definition.find("PopupQuestionNode")
    assert 4 == package_entry.process_def_index(popup_question)
    assert "noCustomersFound"== popup_question.attrib['name']
    assert "noCustomersFound"== popup_question.get('displayName')
    assert "198"== popup_question.attrib['x']
    assert "48"== popup_question.attrib['y']

    package_entry.replace_node_ref(popup_question, "MessageDialog")

    assert not list(package_entry.iter("PopupQuestionNode"))
    message_dialog= package_entry.process_definition.find("ChildProcess")
    assert 4 == package_entry.process_def_index(message_dialog)
    assert "noCustomersFound" == message_dialog.attrib["name"]
    assert "198"== message_dialog.attrib['x']
    assert "48"== message_dialog.attrib['y']
    assert ""== message_dialog.get('displayName')
    assert "false"== message_dialog.get('executeAsAsynchronous')
    assert "false"== message_dialog.get('waitOnParent')
    assert "MessageDialog" == message_dialog.find("ProcessDefinitionReference").attrib["name"]

def test_process_definition(fs):
    source=full_path("processExamples/MainProcess/ValidationProcess.xml")
    fs.add_real_file(source)
    process_definition = SourceObjectParser().parse(source)
    assert None is not process_definition.root.find("ProcessDefinition")
