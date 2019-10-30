import sys
import argparse
from core.visitors import SourceCodeVisitor
import lxml.etree as ET
import logging
from logging.handlers import RotatingFileHandler

no_process_found_msg="No processes found containing PopupQuestions"

def make_data_flow_entry(data_flow,cdata,field_definition_ref):
    data_flow_entry = ET.SubElement(data_flow,"DataFlowEntry")
    from_field=ET.SubElement(data_flow_entry,"FromField")

    parameter_assigment=ET.SubElement(from_field,
                                      "ParameterAssignment",
                                      exceptionStrategy="0",
                                      language="EcmaScript",
                                      name="",
                                      version=""
                                      )
    verbatim=ET.SubElement(parameter_assigment,
                           "Verbatim",
                           fieldName="text")
    verbatim.text ="<![CDATA["+cdata+"]]>"
    to_field=ET.SubElement(data_flow_entry,"ToField")
    to_field=ET.SubElement(to_field,
                           "FieldDefinitionReference",
                           name=field_definition_ref)

class PopupReplacer(SourceCodeVisitor):
    def __init__(self,logger=None):
        self.logger =logger
        self.result=[]

    def replace(self, filepath=None,file_with_paths=None):
        processes =self.visit(filepath,file_with_paths)
        if processes:
            self.logger.info(str(len(processes))+" Processes found containing PopupQuestions")
        else:
            self.logger.info(no_process_found_msg)

    def visit_PackageEntry(self,package_entry):
        self.result.extend(PackageEntryPopupReplacer(package_entry,self.logger).replaceall())
        return self.result

    def visit_ProcessDefinition(self,process_def):
        self.result.extend(ProcessDefinitionPopupReplacer(process_def,self.logger).replaceall())
        return self.result
    def visit_FormProcess(self,form_process):
        self.result.extend(FormProcessPopupReplacer(form_process,self.logger).replaceall())
        return self.result

class BasePopupReplacer(object):
    def __init__(self,base_process_definition,logger=None):
        self.base_process_def = base_process_definition
        self.logger =logger

    @property
    def process_definition(self):
        return self.base_process_def.process_definition

    def replaceall(self):
        result =[]
        popups= self.process_definition.findall("PopupQuestionNode")
        for popup_question_node in popups:
            if popup_question_node is not None:
                self.import_new_popup()
                self.replace_popup(self.base_process_def,popup_question_node,"MessageDialog")

            self.base_process_def.save()

        if popups:
            result.append(self.base_process_def)
            self.logger.info("Replacing "+str(len(popups))+" popup(s) for '"+self.base_process_def.filepath+"'")
        return result

    def filterOKPopups(self,popup_nodes):
        for popup in popup_nodes:
            positiveButton =popup_question.find("PositiveButton").get("text")
            negativeButton =popup_question.find("NegativeButton").get("text")
            if positiveButton and negativeButton:
                btn_combi = negativeButton.strip() + positiveButton.strip()
                #if btn_combi.upper() == "OK":

    def replace_popup(self,process_definition, popup_question_node,new_name):
        message_dialog =process_definition.replace_node_ref(popup_question_node,"MessageDialog")
        process_definition =process_definition.process_definition
        field_store =self.get_field_store_for(process_definition,message_dialog)

        data_flow =ET.SubElement(process_definition,"DataFlow")
        from_node = ET.SubElement(data_flow,"FromNode",name="fieldStore0")
        to_node = ET.SubElement(data_flow,"ToNode",name=message_dialog.get("name"))
        make_data_flow_entry(data_flow,
                             '"'+popup_question_node.get("text")+'"',
                             "line1")
        make_data_flow_entry(data_flow,
                             self.get_message_type(popup_question_node),
                             "messageType")

        node_list = ET.SubElement(data_flow,"GraphNodeList",name="")
        node_x =str(int(popup_question_node.get("x")))
        node_y =str(int(field_store.get("y")))
        ET.SubElement(node_list,
                     "GraphNode",
                     icon="",
                     isLabelHolder="true",
                     label="",
                     name="",
                     x=node_x,
                     y=node_y)

    def get_field_store_for(self,process_definition,message_dialog):
        fieldstore = process_definition.find("ThisNode")
        if fieldstore is not None:
            return fieldstore
        else:
            fieldstore_x = str(int(message_dialog.get("x"))-50)
            fieldstore_y = str(int(message_dialog.get("y"))+80)
            return ET.SubElement(process_definition,"ThisNode",displayName="",name="fieldStore0",x=fieldstore_x,y=fieldstore_y)

    def get_message_type(self,popup_question_node):
        question_type =popup_question_node.get("question").strip()
        if question_type=="Error":
            return "MessageDialog.ERROR_TYPE"
        elif question_type=="Warning":
            return "MessageDialog.WARNING_TYPE"
        else:
            return "MessageDialog.INFORMATION_TYPE"

class FormProcessPopupReplacer(BasePopupReplacer):
    def __init__(self,base_process_definition,logger=None):
        super().__init__(base_process_definition,logger)

    def import_new_popup(self):
        self.base_process_def.add_import("FrameworkCommon.API.PopUpQuestion.MessageDialog")

class ProcessDefinitionPopupReplacer(BasePopupReplacer):
    def __init__(self,base_process_definition,logger=None):
        super().__init__(base_process_definition,logger)

    def import_new_popup(self):
        main_process =self.base_process_def.get_main_process()
        main_process.add_import("FrameworkCommon.API.PopUpQuestion.MessageDialog")
        main_process.save()

class PackageEntryPopupReplacer(BasePopupReplacer):
    def __init__(self,base_process_definition,logger=None):
        super().__init__(base_process_definition,logger)


    def import_new_popup(self):
                self.base_process_def.add_import("FrameworkCommon.API.PopUpQuestion.MessageDialog")


def _build_logger(is_verbose):
        logger =logging.getLogger()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(_build_console_log_handler(formatter,is_verbose))
        logger.addHandler(_build_file_log_handler(formatter))
        return logger

def _build_console_log_handler(formatter,is_verbose):
        console_handler=logging.StreamHandler(sys.stdout)
        if is_verbose:
            logging_level = logging.DEBUG
        else:
            logging_level = logging.INFO
        console_handler.setLevel(logging_level)
        console_handler.setFormatter(formatter)
        return console_handler

def _build_file_log_handler(formatter):
        file_handler=RotatingFileHandler(
                                        "replace_popups.log",
                                        maxBytes=10*1024*1024,
                                        backupCount=2)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        return file_handler

def replace():
    parser = argparse.ArgumentParser()
    parser.add_argument("filesystem_path",nargs='?')
    parser.add_argument("--file-with-paths")
    parser.add_argument("-v",action="store_true")
    args =parser.parse_args()
    filesystem_path = args.filesystem_path
    file_with_paths = args.file_with_paths
    verbose =""
    if len(sys.argv) >2:
        verbose = sys.argv[2]
    logger = _build_logger(args.v)
    popup_replacer = PopupReplacer(logger)
    popup_replacer.replace(filesystem_path,file_with_paths)

if __name__ == "__main__":
    replace()
