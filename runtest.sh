#!/bin/bash - 
#===============================================================================
#
#          FILE: runtest.sh
# 
#         USAGE: ./runtest.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 28/10/19 17:24
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error
cp -r /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test/SimpleValidationQuestionPopup.xml test/processExamples/simple/SimpleValidationQuestionPopup1.xml
python use_cases/popup_replacer.py ~/dev/python/cedtask/test/processExamples/simple/SimpleValidationQuestionPopup1.xml
cp test/processExamples/simple/SimpleValidationQuestionPopup1.xml  /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test/

