#!/bin/bash
#
# bash wrapper around sqlite3 script to use createdView and a table with
# column names to produce a csv file with temperature history
#
cat << EOF |
.mode csv
select * from thColNames;
select * from tempHist;
EOF
sqlite3 /home/nicci/db/temphist.sqlite3
