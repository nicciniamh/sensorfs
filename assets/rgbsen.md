# Example output "sensor"

This is a Sensor derived device that controls a RGB LED using gpiozero. 

Unlinke the read-only devices defined here, this one works a bit differently. The key differences 
are: 

* When sensor data changes, dataToFs is used to export the sensor data to the sensor filesystem
* Runs as its own *collector* 
* Runs as a system service using systemd. 
* The service code waits on data from a FIFO to supply data to write to the device.

To write to this device, writing a  3 digit pair of decimale integers representing red, green and blue values are written to */sensor/pi4/rgb/writer*. E.g., ```echo 42,0,42 >/sensor/pi4/rgb/writer``` will change the colors of the LED to purple. 

The data can be modified through the [REST API Server](assest/restapi.md) with a command like:
```
http(s)://<server>/write?host=<host>&sensor=rgb&data=42,0,42
```

If this sensor is read using, standard sensor interfaces, the return data, in JSON format lookes like

```json

{"modinfo": "com.ducksfeet:gpio:rgb:v0.1", "description": "PWM RGB LED", "time": 1699952837, "rgb": [42, 0, 042]}
```

```python
import os
import sys
import time
import stat
import json
import signal
import argparse
from gpiozero import RGBLED
import sensor
from sensorfs import dataToFs
from rgbconf import rgbPins, rgbAdjust


logfile = None
debugEnabled = False

def debug(*args):
	global debugEnabled
	if debugEnabled:
		log('--debug--',*args)
def log(*args):
	global logfile
	tstr = time.strftime('%D %T -',time.localtime())
	if not logfile:
		print(tstr,*args);
	else:
		with open(logfile,'a') as f:
			print(tstr,*args,file=f)

class rgbLED(sensor.Sensor):
	"""
	A Sensor derived class to control an RGB Led

	This sensor is a little different because it creates it's own sensor fs path
	and creates a fifo within. A thread is created to read the fifo for data and 
	the apply to the hardware. 
	"""
	def __init__(self,name,pins,**kwargs):
		self.senfsPath = None
		self.monitorPath = None
		if 'senfs' in kwargs and kwargs['senfs']:
			host = os.uname()[1].split('.')[0]
			self.monitor = True
			self.senfsPath = os.path.join(kwargs['senfs'],host,name)
			os.makedirs(self.senfsPath,exist_ok=True)
			self.monitorPath = os.path.join(self.senfsPath,'writer')
		super().__init__(name,self._reader,self._writer)
		self.led = RGBLED(*pins)
		self.data = {
			'modinfo': 'com.ducksfeet:gpio:rgb:v0.1',
			'description': 'PWM RGB LED',
			'time': int(time.time()),
			'rgb': [0,0,0]
		}
		self._pindata((0,0,0))
		self._export()

	def _writer(self,data):
		rdata = {
			'modinfo': 'com.ducksfeet:gpio:rgb:v0.1',
			'description': 'PWM RGB LED',
		}
		if type(data) is not dict:
			raise ValueError('expecting a dictionary')
		try:
			rgb = data['rgb']
			rdata['rgb'] = rgb
		except KeyError: 
			raise ValueError('no rgb key in passed value')

		self._pindata(rgb)
		rdata['time'] = int(time.time())
		self.data = rdata
		if self.senfsPath:
			self._export()
		return rdata

	def _pindata(self,rgb):
		rgb = list(rgb)
		for i in range(0,3):
			rgb[i] = rgbAdjust[i](rgb[i])
		def dv(i):
			return (i/256)
		debug(f'Writing rgb data {rgb} to pins')
		self.led.color = tuple(map(dv,rgb))


	def _reader(self):
		if self.senfsPath:
			self._export()
		return self.data

	def _export(self):
		sp = f"/{self.senfsPath.split('/')[1]}"
		host = os.uname()[1].split('.')[0]
		dataToFs(sp,host,self.name,self.data)

if __name__ == "__main__":
	def monitor(sen):
		'''
		this is a function that runs as a thread to monitor the 
		named pipe (fifo) and reads JSON data from it. It's then handed off 
		to super().write() to modify the hardware.
		'''
		def signalHandler(sig,frame):
			log(f'Signal {signal.strsignal(sig)} - exiting')
			if os.path.exists(sen.monitorPath):
				os.unlink(sen.monitorPath)
			sys.exit(0)

		sigs = [
			signal.SIGABRT,
			signal.SIGHUP,
			signal.SIGINT,
			signal.SIGPIPE,
			signal.SIGQUIT,
			signal.SIGTERM
		]
		for s in sigs:
			signal.signal(s,signalHandler)

		log(f"rgbMonitoDaemon pid {os.getpid()}")
		try:	
			if os.path.exists(sen.monitorPath):
				os.unlink(sen.monitorPath)
			os.mkfifo(sen.monitorPath,mode=0o666)
			os.chmod(sen.monitorPath,0o666)
		except Exception as e:
			log(f'{e} checking/Creating fifo on {sen.monitorPath}')
			return
		if not stat.S_ISFIFO(os.stat(sen.monitorPath).st_mode):
			raise IOError(f'the path supplied, {sen.monitorPath}, is not a named pipe')
			return
		while True:
			with open(sen.monitorPath) as f:
				line = str(f.read().strip().split('\n')[0])
				if len(line):
					try:
						r,g,b = map(int,line.split(',',2))
						data = {'rgb': (r,g,b)}
						sen.write(data)
					except Exception as e:
						log(f'monitor exception {e}')
						continue

	parser = argparse.ArgumentParser(description="sensor/daemon for rgb widget")
	parser.add_argument('-d','--debug',action='store_true', default=False)
	parser.add_argument('-l','--logfile',type=str, metavar='logfile', default=None)
	args = parser.parse_args()
	debugEnabled = args.debug
	if args.logfile:
		logfile = args.logfile
	sen = rgbLED('rgb',rgbPins,senfs=f'/sensor')
	monitor(sen)
```
