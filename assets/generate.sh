#!/bin/bash
# this script generates graphs and copies data to where it's needed

set -e
cd ~/db
python histread.py 
cp histblack.jpg /webroot/pi4/docs/temphist
bash runtemphist.sh >history.csv 
cp history.csv /webroot/temphist
