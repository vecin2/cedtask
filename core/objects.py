import xml.etree.ElementTree as ET
import importlib
import os

from core.xml import indent

class SourceObjectParser(object):
    def parse(self,filepath):
        tree =ET.parse(filepath)
        ced_object = self.parse_xml_tree(tree)
        ced_object.filepath = filepath
        return ced_object

    def parse_xml_tree(self,tree):
        module = importlib.import_module("core.objects")
        class_ = getattr(module, tree.getroot().tag)
        return class_(tree)


def full_path(relative_path):
    script_dir =os.path.dirname(__file__)
    return script_dir+"/"+relative_path

class BaseProcessDefinition(object):
    def __init__(self,tree=None,filepath=None):
        self.tree =tree
        self.root = tree.getroot()
        self.filepath=filepath
        self.doc_type = "ProcessDefinition"

    def iter(self,node_name):
        return self.root.iter(node_name)

    def add_node(self,node):
        self.root.find("ProcessDefinition").insert(0,node)

    def imports(self):
        import_declarations = self.root.iter("ImportDeclaration")
        result =[]
        for import_declaration in import_declarations:
            result.append(self.import_path(import_declaration))
        return result

    def import_path(self,import_declaration):
        packages =""
        for package_name in import_declaration.iter("PackageName"):
            if packages:
                packages +="."
            packages += str(package_name.attrib['name'])
        package_entry_ref=list(import_declaration.iter("PackageEntryReference"))[0]
        return packages +"."+ package_entry_ref.attrib["name"]
    """"""
    def replace_node_ref(self,old_node,new_ref_name):
        index =self.process_def_index(old_node)
        self.process_definition.remove(old_node)
        child_process =ET.Element("ChildProcess",
                                  displayName="",
                                  executeAsAsynchronous="false",
                                  name=old_node.get("name"),
                                  waitOnParent="false",
                                  x=old_node.get('x'),
                                  y=old_node.get('y'))
        ET.SubElement(child_process,"ProcessDefinitionReference",name=new_ref_name)
        self.process_definition.insert(index,child_process)
        return child_process

    def process_def_index(self, element):
        for index in range(0,len(self.process_definition)):
                if self.process_definition[index] ==element:
                    return index
        return None

    def save(self):
        header=('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<!DOCTYPE '+self.doc_type+' [] >\n')
        indent(self.root,2)
        root_str=ET.tostring(self.root,encoding='unicode')
        xml_doc=header +root_str
        with open(self.filepath,"w") as xml_file:
            xml_file.write(xml_doc)

class FormProcess(BaseProcessDefinition):
    def __init__(self,tree=None,filepath=None):
        super().__init__(tree)
        self.process_definition = self.root.find("ProcessDefinition")
    def add_packages(self,path_array,package_specifier):
        del path_array[-1]
        for packagename in path_array:
            ET.SubElement(package_specifier,
                          "PackageName",
                          name=packagename)

    def add_package_specifier(self,import_declaration,path_array,name):
        package_specifier =ET.SubElement(import_declaration,
                  "PackageSpecifier",
                  name="")
        self.add_packages(path_array,package_specifier)

    def add_import(self,path,name=None):
        path_array= path.split(".")
        if not name:
            name =path_array[-1]
        import_declaration =ET.Element("ImportDeclaration",
                                       name=name)
        self.add_package_specifier(import_declaration,path_array,name)
        ET.SubElement(import_declaration,
                      "PackageEntryReference",
                      name=name)
        indent(import_declaration,2)
        self.root.insert(0,import_declaration)

class ProcessDefinition(BaseProcessDefinition):
    def __init__(self,tree=None,filepath=None):
        super().__init__(tree)
        self.process_definition = self.root

    def get_main_process(self):
        return self._get_outer_process(self.filepath)

    def _get_outer_process(self,filepath):
        parent_folder=os.path.dirname(filepath)
        if filepath == parent_folder:
            return None
        if os.path.isfile(parent_folder+".xml"):
            ced_object = SourceObjectParser().parse(parent_folder+".xml")
            if type(ced_object) is PackageEntry:
                return ced_object
        return self._get_outer_process(parent_folder)


class PackageEntry(BaseProcessDefinition):
    def __init__(self,tree=None,filepath=None):
        super().__init__(tree)
        process_definition = self.root.find("ProcessDefinition")
        if  process_definition:
            self.process_definition =process_definition
        else:
            self.process_definition = self.root.find("FormProcess")
            self.doc_type ="FormProcess"

    def add_packages(self,path_array,package_specifier):
        del path_array[-1]
        for packagename in path_array:
            ET.SubElement(package_specifier,
                          "PackageName",
                          name=packagename)

    def add_package_specifier(self,import_declaration,path_array,name):
        package_specifier =ET.SubElement(import_declaration,
                  "PackageSpecifier",
                  name="")
        self.add_packages(path_array,package_specifier)

    def add_import(self,path,name=None):
        path_array= path.split(".")
        if not name:
            name =path_array[-1]
        import_declaration =ET.Element("ImportDeclaration",
                                       name=name)
        self.add_package_specifier(import_declaration,path_array,name)
        ET.SubElement(import_declaration,
                      "PackageEntryReference",
                      name=name)
        indent(import_declaration,2)
        self.root.insert(0,import_declaration)



