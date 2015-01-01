#!/bin/bash
# m h  dom mon dow   command
# 0 0   *   *   *    stat.sh

cd $(dirname $0)
path="$(pwd)"
stat_file=project_report

exec 1>>$path/$stat_file
echo "Date: $(date)"
echo "Java Source File Number: $(find . -name *.java  |wc -l)"
echo "Codes Line Number: $(find . -name *.java | xargs cat | wc -l)"
