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
cp /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test/SimpleValidationQuestionPopup.xml test/processExamples/simple/SimpleValidationQuestionPopup1.xml
cp -r /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test/MultiplePopups.xml test/processExamples/simple/MultiplePopups1.xml

python use_cases/popup_replacer.py --file-with-paths=./paths.txt

cp test/processExamples/simple/MultiplePopups1.xml  /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test
cp test/processExamples/simple/SimpleValidationQuestionPopup1.xml  /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test/

