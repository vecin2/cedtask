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
cp -r /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test/FormProcessQuestionPopup.xml test/processExamples/simple/FormProcessQuestionPopup1.xml
rm -rf test/processExamples/simple/FormProcessQuestionPopup1
cp -r /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test/FormProcessQuestionPopup test/processExamples/simple/FormProcessQuestionPopup1
python use_cases/popup_replacer.py ~/dev/python/cedtask/test/processExamples/simple/FormProcessQuestionPopup1.xml
cp test/processExamples/simple/FormProcessQuestionPopup1.xml  /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test/
rm -rf /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test/FormProcessQuestionPopup1
cp -r test/processExamples/simple/FormProcessQuestionPopup1  /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test/
