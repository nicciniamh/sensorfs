# Fan Control API
The fan control API is very simple. It provides two sensors, cpu_fan and cpu_info. The server is implemented in [fanconrol.py](fancontrol.py)

***Caveat***: *Fan control is less useful when an automated service is controlling the fan on the target, for example, [pi5-fan-control](https://github.com/nicciniamh/pi5-fan-control)

The purpose of the API server is to allow for control of this resource remotely. The code presented offers nothing in terms of security. While this is acceptable in my home environment, this is not an ideal outside world implementation. 

The algorhythm of the fan control is simple, 

1. Get cpu temperature
2. check against pre-set limmits
3. adjust fan based on limit
4. repeat

# Sensors and Features

The fan control api presents two sensors, cpu_info and cpu_fan. These sensors have the following features: 

|Capability|cpu_fan   |cpu_info |
|-------------|-------|---------|
| cpu_temp    |   ✔︎   |     ✔︎  |
| cpu_load    |       |     ✔︎  |
| core usage  |       |     ✔︎  |
| sysem ram   |       |     ✔︎  |
| fan_control |   ✔︎   |        |


The full dataset returned by reading cpu_fan is:

```json
{
   "name" : "cpu_fan",
   "rpm" : 3040,
   "speed" : "FanSpeed.MEDIUM",
   "temp" : 56.585,
   "time" : 1722213816
}
```

The full dataset returned by reading cpu_info is:

```json
{
   "boot_time" : 1122015.19,
   "core0" : 0,
   "core1" : 0,
   "core2" : 100,
   "core3" : 1.3,
   "cputemp" : 66.705,
   "loadavg" : 0.96240234375,
   "modinfo" : "com.ducksfeet:vsen:cpuinfo:v0.4",
   "name" : "cpu_usage",
   "time" : 1722286969,
   "usage" : 25.3,
   "vmem" : 15.7
}
```

## Accessing the API
The API is accessed by making a http request to the system running the api server on port 4243.

Reading: 

`http:pi5.local:4243/read?sensor=cpu_fan`

Writing (for fan control):

`http:pi5.local:4243/write?sensor=cpu_fan&value=1`

Valid values are: 

|Value|Function           |
|-----|-------------------|
|  0  | FanSpeed.OFF      |
|  1  | FanSpeed.LOW      |
|  2  | FanSpeed.MEDIUM   |
|  3  | FanSpeed.HIGH     |
|  4  | FanSpeed.MAX      |

## Example

This is a barebones example of controlling temperature using just http requests. 

```python

import time
import requests

def make_request(command,*args):
	if not command in ['read','write']:
		raise ValueError('Invalid command')
	if command ==  'write' and len(args) < 1:
		raise ValueError("Write needs argument")

	if command == write:
		command = f'{command}?sensor=cpu_temp&value={args[0]}'
	else:
		command = f'{command}?sensor=cpu_temp'
	url = f'http://{self.server}:4243/{command}';
	r = requests.get(url=url, headers=headers)
	try:
		js = r.json()
	except Exception as e:
		raise hsException(_detailedError(e,url,r))
	if type(js) is str:
		d = json.loads(js)
	else:
		d = js
	return d

while True:
	data = make_request('read')
	temp = data['temp']
	if temp >= 70:
		spd = 4
	elif temp >= 65:
		spd = 3
	elif temp > 60:
		spd = 2
	elif temp > 55:
		spd = 1
	else:
		spd = 0
	make_request('write',spd)
	time.sleep(2)
```
