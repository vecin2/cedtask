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
cp -r /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test/MainFormProcess.xml test/processExamples/simple/MainFormProcess1.xml
rm -rf test/processExamples/simple/MainFormProcess1
cp -r /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test/MainFormProcess/ test/processExamples/simple/MainFormProcess1
python use_cases/popup_replacer.py ~/dev/python/cedtask/test/processExamples/simple/MainFormProcess1
cp test/processExamples/simple/MainFormProcess1.xml  /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test
rm -rf /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test/MainFormProcess1
cp -r test/processExamples/simple/MainFormProcess1/  /opt/em/projects/Pacificorp/trunk/repository/default/ReadsInvoicesUsage/Test

