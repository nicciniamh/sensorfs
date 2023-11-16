# Sen2Fs - Export a dict by property to sensorFS

This function explodes a dict into files based on basepath, dataclass and data. So with a dict 
representing data from an AHT10 sensor on Pi3, storing in the base path of sensor, the call would 
look like ```dataToFs('/sensor/pi3','aht10', data)```. 
Given the dictionary:

```
{
	"description": "AOSONG AHT10/AHT20",
	"modinfo": "com.ducksfeet:i2cdev:aht10:v0.5",
	"tempc": 23.76,
	"temp": 74.768,
	"humidity": 58.974444444444444,
	"time": 1699651307,
	"name": "aht10"
}
``` 

This would result in a directory in /sensor/pi3/aht10 with the following files:

```
/sensor/pi3/aht10/
├── aht10.json
├── description
├── humidity
├── modinfo
├── name
├── temp
├── tempc
└── time

```

Each file contains data specific to that item. temp, tempc, and humidity are the readings from the sensor. 
Time is contains the time the last reading was taken and description and modinfo are both informational. Finally, name is the name of the sensor as defined when instantiated. 


```python
import os
import json

def dataToFs(basepath,dataclass,data):
	'''
	Recursively create data nodes in sensorfs
	basepath: e.g, /sensor/pi4
	dataclass: type of data, e.g., sensor name
	data: dict of data
	each element would be in /basepath/dataclass/element
	'''
	os.makedirs(basepath,exist_ok=True)
	for k,v in data.items():
		if type(v) is dict:
			dp = os.path.join(basepath,k)
			os.makedirs(dp,exist_ok=True)
			dataToFs(dp,k,v)
		else:
			fn = os.path.join(basepath,k)
			with open(fn,'w') as f:
				if k == 'error':
					f.write(f'error: {v}, data: {data}\n')
				else:
					f.write(f'{v}\n')

	with open(os.path.join(basepath,f'{dataclass}.json'),'w') as f:
		json.dump(data,f)
```
