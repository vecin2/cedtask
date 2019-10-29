import xml.etree.ElementTree as ET
import sys
import os
from collections import defaultdict

def find_popup(filepath):
    result=defaultdict(list)
    exclude_directories = set(['Resources']) 
    for dirpath, dirnames, files in os.walk(filepath):
        dirnames[:] = [d for d in dirnames if d not in exclude_directories]
        for name in files:
            print(dirpath+name)
            if name.lower().endswith(".xml"):
                filepath=os.path.join(dirpath, name)
                tree = ET.parse(filepath)
                root_tag= tree.getroot().tag
                list_popups =list(tree.iter("PopupQuestionNode"))
                if list_popups:
                    if not list(tree.iter("DataFlow")):
                        popup_question= list_popups[0]
                        positiveButton =popup_question.find("PositiveButton")
                        negativeButton =popup_question.find("NegativeButton")
                        key = root_tag +\
                               positiveButton.attrib['text'].strip() +\
                               negativeButton.attrib['text'].strip()+\
                               popup_question.attrib['question']
                        result[key].append(filepath)
    return result
def main():
    path =sys.argv[1]
    results = find_popup(path)
    if not os.path.exists("results"):
        os.makedirs("results")
    for key,value in results.items():
        with open("results/"+key+".txt","w") as txt_file:
            for path in value:
                txt_file.write(path+'\n')

    return results

if __name__ == "__main__":
    main()
