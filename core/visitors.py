import os
import xml.etree.ElementTree as ET

from core.objects import ProcessDefinition,SourceObjectParser

class SourceCodeVisitor(object):
    def get_visitor(self, tree):
        method = 'visit_' + tree.getroot().tag
        return getattr(self, method, None)

    def visit(self,filesystem_path=None,file_with_paths=None):
        if filesystem_path:
            return self.visit_path(filesystem_path)
        else:
            return self.visit_file_with_paths(file_with_paths)

    def visit_path(self, filesystem_path):
        exclude_directories = set(['Resources'])
        result = None
        if os.path.isfile(filesystem_path):
            dirpath = os.path.dirname(filesystem_path)
            filename = os.path.basename(filesystem_path)
            return self.visit_file(dirpath,filename)
        for dirpath, dirnames, files in os.walk(filesystem_path):
            dirnames[:] = [d for d in dirnames if d not in exclude_directories]
            for name in files:
                result =self.visit_file(dirpath,name)
        return result

    def visit_file_with_paths(self,file_with_paths):
        result =[]
        with open(file_with_paths,'r') as f:
            for line in f:
                line_content=line.rstrip('\n')
                result = self.visit_file(os.path.dirname(line_content),os.path.basename(line_content))
        return result
    def visit_file(self,dirpath,name):
        if name.lower().endswith(".xml"):
            filepath=os.path.join(dirpath, name)
            tree=ET.parse(filepath)
            f = self.get_visitor(tree)
            if f is not None:
                ced_object=SourceObjectParser().parse_xml_tree(tree)
                ced_object.filepath=filepath
                return f(ced_object)
            return None

