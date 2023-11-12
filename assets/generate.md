# generate.sh

```bash
#!/bin/bash
# this script generates graphs and copies data to where it's needed

set -e
cd ~/db
python histread.py 
cp histblack.jpg /webroot/pi4/docs/temphist
bash runtemphist.sh >history.csv 
cp history.csv /webroot/temphist
```
---

<small>This page, images and code are Copyright &copy; 2023 [Nicole Stevens](/sensorfs/about.html) All rights reserved.</small>
