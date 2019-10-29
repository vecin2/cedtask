import xml.etree.ElementTree as ET
import sys
import os
from collections import defaultdict
import logging
from logging.handlers import RotatingFileHandler

class WebTextfieldVisitor(object):
    webtxtfield_repre = {'name': 'GT_WEBTextField', 'platform': 'GT_WEB'}
    def __init__(self,logger=None):
        self.logger =logger

        self.forms={}
        self.forms_changed=defaultdict(list)
        self.compose_form =None

    def visit_compose(self,compose_form):
        self.compose_form =compose_form
        for form in compose_form:
            self.visit(form)
        changed_forms =[form for form in self.forms.values() if form.filepath in self.forms_changed] 
        return ComposeForm(logger=self.logger,forms=changed_forms)

    def visit(self,form):
        self.forms[form.filepath]= form
        for textfield in form.textfields.values():
            if "GT_WEB" not in textfield.representations:
                self.forms_changed[form.filepath].append(textfield.name())
                textfield.add_representation(self.webtxtfield_repre)
    def log_stats(self):
        StatsLogger(self,self.logger).log_stats(self.compose_form.folderpath)

class StatsLogger(object):
    def __init__(self, repre_visitor,logger):
        self.forms= repre_visitor.forms
        self.forms_changed= repre_visitor.forms_changed
        self.logger = logger
    def log_stats(self,folderpath):
        self.log_totals(folderpath)
        self.log_changes()

    def log_totals(self,folderpath):
        self.logger.info("Found "+str(len(self.forms))+" forms under "+folderpath)
        self.logger.info(str(len(self.forms_changed))+" Forms out of "+str(len(self.forms))+" were changed")
        textfields_changed =[len(textfields) for textfields in self.forms_changed.values()]
        self.logger.info(str(sum(textfields_changed))+" textfields changed in total")

    def log_changes(self):
        for filename,form in self.forms.items():
            self.logger.debug("Form "+filename+" has "+str(len(form.textfields))+" Textfields")
            if filename in self.forms_changed:
                self.logger.debug("Representation was added to the following Texfields:"\
                +str(self.forms_changed[filename]))

class FormComponent(object):
    def __init__(self,root):
        self.root =root

    def name(self):
        return self.root.attrib["name"]

    @property
    def representations(self):
        _representations ={}
        for repre in self.root.iter("RepresentationReference"):
            _representations[repre.attrib['platform']]=repre
        return _representations

    def add_representation(self,attribs):
                ET.SubElement(self.root,
                              "RepresentationReference",
                              attribs)

class TextField(FormComponent):
    def __init__(self,root):
        super().__init__(root)

class Form(FormComponent):
    def __init__(self,filepath,logger=None):
        self.filepath = filepath
        self.tree = ET.parse(filepath)
        self.root = self.tree.getroot()
        self._listboxes =None
        self._textfields =None
        self.logger =logger


    def listboxes(self):
        if not self._listboxes:
            self._listboxes=[]
            for listbox in self.root.iter("ListBox"):
                self._listboxes.append(ListBox(listbox))
        return self._listboxes

    @property
    def textfields(self):
        if not self._textfields:
            self._textfields={}
            for xml_textfield in self.root.iter("TextField"):
                textfield =TextField(xml_textfield)
                self._textfields[textfield.name()]=textfield
        return self._textfields

    def contains_list(self):
        return len(self.listboxes())>0

    def write(self):
        header=('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<!DOCTYPE Form [] >\n')
        root_str=ET.tostring(self.root,encoding='unicode')
        xml_doc=header +root_str
        with open(self.filepath,"w") as xml_file:
            if self.logger:
                self.logger.debug("Overwriting file '"+self.filepath+"'")
            xml_file.write(xml_doc)

class ComposeForm(Form):
    def __init__(self,folderpath=None,logger=None,forms=None):
        self.folderpath = folderpath
        self._forms =forms
        self.logger = logger

    def __len__(self):
        return len(self.forms)

    def __iter__(self):
        return iter(self.forms)

    @property
    def forms(self):
        if self._forms is None:
            self._load_forms()
        return self._forms

    def _load_forms(self):
        self._forms =[]
        for dirpath, dirnames, files in os.walk(self.folderpath):
            for name in files:
                if name.lower().endswith(".xml"):
                    filepath=os.path.join(dirpath, name)
                    tree = ET.parse(filepath)
                    if tree.getroot().tag=="Form":
                        self.append(Form(filepath,self.logger))
        return self._forms

    def append(self,form):
        if not self._forms:
            self._forms =[]
        self._forms.append(form)

    @property
    def textfields(self):
        result = {}
        for form in self.forms:
            result.update(form.textfields)
        return result

    @property
    def representations(self):
        result = {}
        for form in self.forms:
            result.update(form.representations)
        return result

    def write(self):
        self.logger.info("Writing Forms to disk...")
        for form in self.forms:
            form.write()
        self.logger.info(str(len(self.forms)) +" Forms wrote to disk")


def main(logger=None):
    path =sys.argv[1]
    verbose = False
    if len(sys.argv) >2:
        verbose = sys.argv[2]
    if not logger:
        logger = _build_logger(verbose=="-v")
    print ("Running Sanitizer for path "+path)
    composeForm = ComposeForm(path,logger)
    visitor =WebTextfieldVisitor(logger)
    changed_formset = visitor.visit_compose(composeForm)
    visitor.log_stats()
    if len(changed_formset)>0:
        if "Y" ==input("Do you want to write these changes to disk(Y/N)? "):
            print("Overwriting files...")
            changed_formset.write()
        else:
            logger.info("Changes discarded")

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

if __name__ == "__main__":
    main()
