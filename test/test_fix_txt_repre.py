import os
import sys
import pytest
from io import StringIO
from test.utils.fake_logging import FakeLogger
import os
from fix_txtfield_repr import ComposeForm,Form,WebTextfieldVisitor,main

osep=str(os.sep)


class WebTextfieldFixer(object):
    def __init__(folderpath):
        self.folderpath = folderpath

def setup_fs(fs,filenames):
    script_dir =os.path.dirname(__file__)
    examples_dir=script_dir+osep+"formExamples"
    for filename in filenames:
        filepath = os.path.join(examples_dir,filename)
        fs.add_real_file(filepath,False,"repo"+osep+filename)

@pytest.fixture
def form(fs):
    setup_fs(fs,["FormExample.xml"])
    yield Form("repo"+osep+"FormExample.xml")

def test_textfields(form):
    textfields = form.textfields
    assert 3 == len(textfields)
    textfield =textfields['txtAddress']
    repre =textfield.representations['Gecko']
    expected_attrib = {'name': 'GeckoTextField', 'platform': 'Gecko'}
    assert expected_attrib == repre.attrib


webtxtfield_repre = {'name': 'GT_WEBTextField', 'platform': 'GT_WEB'}

def test_add_webtextfield_repre(form):
    textfields = form.textfields
    textfield =textfields['txtCity']
    assert "GT_WEB" not in textfield.representations
    WebTextfieldVisitor().visit(form)
    assert  webtxtfield_repre == textfield.representations["GT_WEB"].attrib

def test_dont_addwebtextfield_repre_when_already_present(form):
    textfields = form.textfields
    textfield =textfields['txtState']
    assert "GT_WEB" in textfield.representations
    WebTextfieldVisitor().visit(form)
    assert  webtxtfield_repre == textfield.representations["GT_WEB"].attrib

def test_write_form_to_disk(form):
    addresstxt = form.textfields["txtAddress"]
    assert "GT_WEB" not in addresstxt.representations
    addresstxt.add_representation(webtxtfield_repre) 
    form.write()
    loaded_form = Form(form.filepath)
    loaded_addresstxt=form.textfields["txtAddress"]
    assert webtxtfield_repre == loaded_addresstxt.representations["GT_WEB"].attrib

def test_reporting(fs):
    setup_fs(fs,["FormExample.xml",
                 "FormExampleNoTxtFields.xml",
                 "FormExampleTwoTxtFields.xml"])
    assert True == os.path.isfile(osep+"repo"+osep+"FormExample.xml")
    assert True == os.path.isfile(osep+"repo"+osep+"FormExampleNoTxtFields.xml")
    assert True == os.path.isfile(osep+"repo"+osep+"FormExampleTwoTxtFields.xml")
    sys.argv=[".",osep+"repo"]
    logger = FakeLogger()

    sys.stdin = StringIO("N\n")
    main(logger=logger)

    assert "INFO Found 3 forms under "+osep+"repo" ==logger.lines[1]
    assert "INFO 2 Forms out of 3 were changed" == logger.lines[2]
    assert "INFO 4 textfields changed in total" == logger.lines[3]
    assert "DEBUG Form "+osep+"repo"+osep+"FormExample.xml has 3 Textfields" == logger.debug_lines[1]
    assert "DEBUG Representation was added to the following Texfields:"\
            "['txtAddress', 'txtCity']" == logger.debug_lines[2]
    assert "DEBUG Form "+osep+"repo"+osep+"FormExampleNoTxtFields.xml has 0 Textfields" == logger.debug_lines[3]
    assert "DEBUG Form "+osep+"repo"+osep+"FormExampleTwoTxtFields.xml has 2 Textfields" == logger.debug_lines[4]
    assert "DEBUG Representation was added to the following Texfields:"\
            "['txtTransactionType', 'txtTotalAmount']" == logger.debug_lines[5]
def test_no_forms(fs):
    logger = FakeLogger()
    main(logger)
    assert "INFO Found 0 forms under "+osep+"repo" ==logger.lines[1]
    assert "INFO 0 Forms out of 0 were changed" == logger.lines[2]
    assert "INFO 0 textfields changed in total" == logger.lines[3]
def test_logger(fs):
    sys.argv=[".",osep+"repo"]
    main()
    sys.argv=[".",osep+"repo","-v"]
    main()

def test_user_cancel_does_not_write_to_disk(fs):
    setup_fs(fs,["FormExampleTwoTxtFields.xml"])
    sys.stdin = StringIO("N\n")
    logger = FakeLogger()
    main(logger)
    form = Form("repo"+osep+"FormExampleTwoTxtFields.xml")
    assert "GT_WEB" not in form.textfields["txtTransactionType"].representations
    assert "GT_WEB" not in form.textfields["txtTotalAmount"].representations

def test_user_confirms_writes_to_disk(fs):
    setup_fs(fs,["FormExampleTwoTxtFields.xml"])
    sys.stdin = StringIO("Y\n")
    logger = FakeLogger()
    main(logger)
    form = Form("repo"+osep+"FormExampleTwoTxtFields.xml")
    assert "GT_WEBTextField" ==form.textfields["txtTransactionType"].representations["GT_WEB"].attrib["name"]
    assert "GT_WEBTextField" ==form.textfields["txtTotalAmount"].representations["GT_WEB"].attrib["name"]

