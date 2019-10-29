import os
import sys
from search_popup_questions import main

osep=str(os.sep)
def find_popup(filepath):
    sys.argv=[".",osep+filepath]
    return main()

def test_path_without_processes():
    results = find_popup("config")
    assert 0 == len(results)

def add_real_file(fs, relative_filepath, fake_path):
    script_dir =os.path.dirname(__file__)
    filename= os.path.basename(relative_filepath)
    full_filepath=script_dir+osep+relative_filepath
    fs.add_real_file(full_filepath,False,fake_path+osep+filename)

process_no_popup_filepath="processExamples"+osep+"SimpleValidationMessageDialog.xml"
process_with_popup_filepath="processExamples"+osep+"SimpleValidationQuestionPopup.xml"
path_without_popup="repo"+osep+"no_question_popup"
path_with_popup="repo"+osep+"with_question_popup"

def test_process_no_popup_question_retrieves_nothing(fs):
    add_real_file(fs,process_no_popup_filepath,path_without_popup)
    results = find_popup(path_without_popup)
    assert 0 == len(results)

def test_process_one_popup_question_retrieves_one(fs):
    add_real_file(fs,process_with_popup_filepath,path_with_popup)
    results = find_popup(path_with_popup)
    assert 1 == len(results)

