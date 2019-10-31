import lxml.etree as ET
import sys
import os
from collections import defaultdict

def find_popup(filepath):
    result=defaultdict(list)
    exclude_directories = set(['Resources'])
    for dirpath, dirnames, files in os.walk(filepath):
        dirnames[:] = [d for d in dirnames if d not in exclude_directories]
        for name in files:
            if name.lower().endswith(".xml"):
                filepath=os.path.join(dirpath, name)
                tree = ET.parse(filepath)
                root_tag= tree.getroot().tag
                list_popups =list(tree.iter("PopupQuestionNode"))
                if list_popups:
                        popup_question= list_popups[0]
                        positiveButton =popup_question.find("PositiveButton")
                        negativeButton =popup_question.find("NegativeButton")
                        positiveButtonText =popup_question.find("PositiveButton").get("text")
                        negativeButtonText =popup_question.find("NegativeButton").get("text")
                        btn_combi = negativeButtonText.strip() + positiveButtonText.strip()
                        tail=""
                        if root_tag == "PackageEntry":
                            if list(tree.iter("FormProcess")):
                                tail="FormProcess"
                        key = root_tag + tail +btn_combi.upper()
                        result[key].append(filepath)
    return result
def main():
    path =sys.argv[1]
    if len(sys.argv) >2:
        folder = sys.argv[2]
    else:
        folder ="results"

    results = find_popup(path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    for key,value in results.items():
        with open(folder+os.sep+key+".txt","w") as txt_file:
            for path in value:
                txt_file.write(path+'\n')

    return results

if __name__ == "__main__":
    main()
