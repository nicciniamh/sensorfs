# histcollect

This script is run once an hour via cron(8). Very simply, it stores data for each
defined sensor in a database with each table as temphist_<host>. Each of the defined keys
are used for the column names on the SQL insert. 


```python
#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
import pprint
import time
sys.path.append(os.path.expanduser('~/lib'))
from senfs2 import senfs

sensors = {
	'piz': {'type': 'dht22', 	'keys': ['temp','humidity','time','hour']},
	'pi3': {'type': 'si7021', 	'keys': ['temp','humidity','time','hour']},
	'pi4': {'type': 'aggregate','keys': ['temp','humidity','pressure','time','hour']},
}

def putSensorHistory(host,rowdata,keys):
	dbf = os.path.expanduser('~/db/temphist.sqlite3')
	values = ','.join(map(str,rowdata))
	coldef = f"({','.join(keys)})"
	with sqlite3.connect(dbf) as con:
		cur = con.cursor()
		sql = f'INSERT INTO temphist_{host} {coldef} VALUES ({values})'
		#print(sql)
		cur.execute(sql)
		if not cur.rowcount:
			raise Exception(f'sqlite3 returned rowcount of zero on insert')
		con.commit()

try:
	for host,sendef in sensors.items():
		sensor = senfs(sendef['type'],host)
		data = sensor.read()
		rowdata = []
		for k in sendef['keys']:
			if k == 'hour':
				rowdata.append(time.localtime(data['time']).tm_hour)
			else:
				rowdata.append(data[k])
 		putSensorHistory(host,rowdata,sendef['keys'])

except Exception as e:
	print(f'histcollect: exception {e}',file=sys.stderr)
```

---

<small>This page, images and code are Copyright &copy; 2023 [Nicole Stevens](/sensorfs/about.html) All rights reserved.</small>
