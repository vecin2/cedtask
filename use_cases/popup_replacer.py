import sys
from core.visitors import SourceCodeVisitor
import xml.etree.ElementTree as ET
import logging
from logging.handlers import RotatingFileHandler

def _escape_cdata(text):
    try:
        if "&" in text:
            text = text.replace("&", "&amp;")
        # if "<" in text:
            # text = text.replace("<", "&lt;")
        # if ">" in text:
            # text = text.replace(">", "&gt;")
        return text
    except TypeError:
        raise TypeError(
            "cannot serialize %r (type %s)" % (text, type(text).__name__)
        )

ET._escape_cdata = _escape_cdata

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

    def replace(self, filepath):
        processes =self.visit(filepath)
        if processes:
            self.logger.info("1 Processes found containing PopupQuestions")
        else:
            self.logger.info(no_process_found_msg)

    def visit_PackageEntry(self,package_entry):
        self.result.extend(PackageEntryPopupReplacer(package_entry).replaceall())
        return self.result

    def visit_ProcessDefinition(self,process_def):
        self.result.extend(ProcessDefinitionPopupReplacer(process_def).replaceall())
        return self.result


class BasePopupReplacer(object):
    def __init__(self,base_process_definition):
        self.base_process_def = base_process_definition

    @property
    def process_definition(self):
        return self.base_process_def.process_definition

    def replaceall(self):
        result =[]
        for popup_question_node in self.process_definition.findall("PopupQuestionNode"):
            if popup_question_node is not None:
                self.import_new_popup()
                result.append(self.base_process_def)
                self.replace_popup(self.base_process_def,popup_question_node,"MessageDialog")

            self.base_process_def.save()

        return result

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
        question_type =popup_question_node.get("question")
        if question_type =="Information":
            return "MessageDialog.INFORMATION_TYPE"

class ProcessDefinitionPopupReplacer(BasePopupReplacer):
    def __init__(self,base_process_definition):
        super().__init__(base_process_definition)

    def import_new_popup(self):
        main_process =self.base_process_def.get_main_process()
        main_process.add_import("FrameworkCommon.API.PopUpQuestion.MessageDialog")
        main_process.save()

class PackageEntryPopupReplacer(BasePopupReplacer):
    def __init__(self,base_process_definition):
        super().__init__(base_process_definition)


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
                                        "update_repre.log",
                                        maxBytes=10*1024*1024,
                                        backupCount=2)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        return file_handler

def replace():
    filesystem_path =sys.argv[1]
    verbose =""
    if len(sys.argv) >2:
        verbose = sys.argv[2]
    logger = _build_logger(verbose=="-v")
    popup_replacer = PopupReplacer(logger)
    popup_replacer.replace(filesystem_path)

if __name__ == "__main__":
    replace()
