import time 
import json
import os
import sys

import sensi7021
from sensorfs import dataToFs

if __name__ == "__main__":
	host = os.uname()[1].split('.')[0]
	s = sensi7021.sensor('si7021')
	while True:
		data = s.read()
		data['temp'] = data['tempf']
		del(data['tempf'])
		dataToFs('/sensor',host,data)
		data['time'] = int(time.time())
		with open(f'/sensor/{host}/tempdata.json','w') as f:
			json.dump(data,f)
		time.sleep(1) ## Don't read too quickly
