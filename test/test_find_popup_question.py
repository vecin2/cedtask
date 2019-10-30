import os
import sys
from shutil import copyfile,rmtree
from search_popup_questions import main
import pytest

osep=str(os.sep)
@pytest.fixture()
def cleandir():
    try:
        script_dir =os.path.dirname(__file__)
        rmtree(script_dir+"/tmp")
    except OSError:
        pass

def full_path(relative_path):
    script_dir =os.path.dirname(__file__)
    original_file = script_dir+"/"+relative_path
    target = script_dir +"/tmp/test_processes/"+ relative_path
    os.makedirs(os.path.dirname(target), exist_ok=True)
    copyfile(original_file,target)
    return target

def find_popup(filepath):
    sys.argv=[".",osep+filepath]
    return main()

def test_path_without_processes():
    results = find_popup("config")
    assert 0 == len(results)


process_no_popup_filepath="processExamples"+osep+"SimpleValidationMessageDialog.xml"
process_with_popup_filepath="processExamples"+osep+"SimpleValidationQuestionPopup.xml"
path_without_popup="repo"+osep+"no_question_popup"
path_with_popup="repo"+osep+"with_question_popup"

@pytest.mark.usefixtures("cleandir")
def test_process_no_popup_question_retrieves_nothing():
    source =full_path(process_no_popup_filepath)
    results = find_popup(source)
    assert 0 == len(results)

@pytest.mark.usefixtures("cleandir")
def test_process_one_popup_question_retrieves_one():
    source =full_path(process_with_popup_filepath)
    results = find_popup(os.path.dirname(source))
    assert 1 == len(results)

