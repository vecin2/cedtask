#!/bin/bash - 
#===============================================================================
#
#          FILE: runMultipleTest.sh
# 
#         USAGE: ./runMultipleTest.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 28/10/19 22:01
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error
cp -r /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test/MultiplePopups.xml test/processExamples/simple/MultiplePopups1.xml
python use_cases/popup_replacer.py ~/dev/python/cedtask/test/processExamples/simple/MultiplePopups1.xml
cp test/processExamples/simple/MultiplePopups1.xml  /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test

