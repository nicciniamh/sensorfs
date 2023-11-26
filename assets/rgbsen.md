# rgbsen.py - Example of I/O sensor

This sensor is a little different because it creates it's own sensor fs path and creates a fifo within. A thread is created to read the fifo for data and the apply to the hardware. Differences between this and other
sensor derived classes: 

* This sensor should not be instantiated directly but commanded through the fifo interface and the *senfs2* module. 
* While producing a *sensor filesystem* sensor interface, this modules is more of a service than a driver.
* This module creates a sensor and acts as it's own collector. 


## Command Interface

This sensor creates a FIFO called writer on it's *sensor file system path*, e.g., /sensor/pi4/rgbsen/writer, which is used to command the background thread of the sensor.

The background thread is running the function in monitor. The only parameter is the sensor object. Monitor reads the fifo for two types of data: rgb values or commands. rgb values are a line with red,green,blue. Commands take the form of @cmd:data. These commands may be broken into subcommands, as is the case with rainbow. 

### Monitor Commands

|Command |Function                                                       |Arguments   |
|--------|---------------------------------------------------------------|------------|
| on     | Turn on LEDs by setting RGB to 255,255,255                    | None       |
| off    | Turn on LEDs by setting RGB to 0,0,0                          | None       |
| rgb    | Set rgb pins value to value in data                           | rgb triplet|
| hsl    | set rgb pins value to hsl value in data                       | hsl triplet|
| rainbow| Turn on color cycling [see below](#Rainbow-Commands)          | see below  |

Note that all but the rainbow commands turn off any active color cycling.

## Rainbow or Color Cycling Mode

The monitor thread can be commanded to start a color cycling mode on the rgb pins by cycling through hues with a changeable saturation and lightness setting. This is accomplished by starting a thread which runs until it's run flag is set to False. Rainbow mode is controlled using the @cmd interface with

    @cmd:rainbow:subcommand:data

# Rainbow Subcommands

| Subcommand | Function                     | Arguments                 |
|------------|------------------------------|---------------------------|
| on         | Turn on color cycling        | None                      |
| off        | Turn off color cycling       | None                      |
| setsatlight| Set saturation and lightness | saturation,lightness pair |


```python
import os
import sys
import time
import stat
import json
import signal
import argparse
import threading
from gpiozero import RGBLED
import sensor
from sensorfs import dataToFs
from rgbconf import rgbPins, rgbAdjust
import colorsys 
import re

logfile = None
debugEnabled = False

logfile = os.path.expanduser('~/.local/logs/rgbsen.log')

def strToRgb(s):
	def cvi(s):
		return int(s)&0xff;
	return list(map(cvi, re.sub("[^0-9,]", "",s).split(',')))

def hslStrToRgb(s):
	def cvi(s):
		return int(s)&0xff;
	hsl = list(map(cvi, re.sub("[^0-9,]", "",s).split(',')))
	for i in range(0,3):
		if i == 0:
			hsl[i] /= 360;
		else:
			hsl[i] /= 100;
	rgb = list(colorsys.hsv_to_rgb(*hsl))
	for i in range(0,3):
		rgb[i] = int(rgb[i]*255)&255
	return rgb


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

class _RainbowThread(threading.Thread):

	def __init__(self,sen):
		self.hue  = 0;
		self.sat = 60;
		self.light = 100;
		self.sen = sen
		self.interval=250
		self.increment = 10;
		self.runFlag = False
		super(_RainbowThread,self).__init__(target=self._runner)

	def start(self):
		self.runFlag = True
		super().start()

	
	def _setSatLight(self,sat=None,light=None):
		if type(sat) is int:
			self.sat = sat
		if type(light) is int:
			self.light = light

	def _runner(self):
		print("Rainbow runner")
		while self.runFlag:
			self.hue += self.increment
			if self.hue >= 360:
				self.hue = 0;
			hsv = [self.hue,self.sat,self.light]
			map(lambda n: n/100,hsv)
			rgb = colorsys.hsv_to_rgb(*hsv)
			map(lambda n: ((n*100)&0xff), rgb)
			self.sen._pindata(hsv)
			time.sleep(self.interval/1000)


class rgbLED(sensor.Sensor):
	"""
	A Sensor derived class to control an RGB Led

	This sensor is a little different because it creates it's own sensor fs path
	and creates a fifo within. A thread is created to read the fifo for data and
	the apply to the hardware. Another difference is this sensor should not
	be instantiated directly but commanded through the fifo interface and
	the senfs2 module.
	"""
	def __init__(self,name,pins,**kwargs):
		self.senfsPath = None
		self.monitorPath = None
		self.rainbow = None
		if 'senfs' in kwargs and kwargs['senfs']:
			host = os.uname()[1].split('.')[0]
			self.monitor = True
			self.senfsPath = os.path.join(kwargs['senfs'],host,name)
			os.makedirs(self.senfsPath,exist_ok=True)
			self.monitorPath = os.path.join(self.senfsPath,'writer')
		super().__init__(name,self._reader,self._writer)
		self.led = RGBLED(*pins)
		self.data = {
			'modinfo': 'com.ducksfeet:gpio:rgb:v0.3.1mt',
			'description': 'PWM RGB LED',
			'time': int(time.time()),
			'rgb': [0,0,0],
			'state': 'off'
		}
		self._pindata((0,0,0))
		self._export()

	def _setstate(self):
		try:
			stin = self.data['state']
		except:
			stin = 'foo'
		if self.rainbow:
			if self.rainbow.runFlag:
				debug(f'rainbowRunFlag {self.rainbow.runFlag}')
				st = 'rainbow'
		else:
			if self.data['rgb'] == [0,0,0]:
				st = 'off'
			else:
				st = 'on'
		if(st != stin):
			self.data['state'] = st
			debug(f'Setting state to {st}')
			self._export()

	def _writer(self,data):
		if type(data) is not dict:
			raise ValueError('expecting a dictionary')
		try:
			rgb = data['rgb']
			self.data['rgb'] = rgb
		except KeyError: 
			raise ValueError('no rgb key in passed value')

		self._pindata(rgb)
		self.data['time'] = int(time.time())
		return self.data

	def _pindata(self,rgb):
		rgb = list(rgb)
		for i in range(0,3):
			rgb[i] = rgbAdjust[i](rgb[i])
		def dv(i):
			return (i/256)
		self.data['rgb'] = rgb
		debug(f'Writing rgb data {rgb} to pins')
		self.led.color = tuple(map(dv,rgb))
		if self.senfsPath:
			self._export()
		self._setstate()

	def doCommand(self,cmd, data):
		''' do a command handed off from monitor
		    commands are @cmd:<cmd><data>
			cmd can be:
				<on|off> - turn on or off the leds with 0,0,0 or 255,255,255
				<rgb|hsl> - set the leds to the rbg or hsl value in 'data'
				rainbow>:cmd:data
					cmd:	on|off|setsatlight
						<on|off> - turn color cycling on or off
						setsatlight - set saturation and lightness to values in 'data'.
		'''
		cmd = cmd.lower()
		if cmd == 'rainbow':
			self.rainbowCmd(data)
		elif cmd == 'on':
			self.On()
		elif cmd == 'off':
			self.Off()
		elif cmd == 'rgb' or cmd == 'hsl':
			if cmd == 'rgb':
				debug('rgbdata')
				self._pindata(strToRgb(data))
			elif cmd == 'hsl':
				debug('hsvdata')
				self._pindata(hslStrToRgb(data))

	def rainbowCmd(self,data):
		if ':' in data:
			sc,data = data.split(':',1)
		else:
			sc = data
			data = ''

		debug(f'rainbowCmd: subcommand {sc}, data {data}')
		if sc == 'on':
			if not self.rainbow:
				self.rainbow = _RainbowThread(self)
				self.rainbow.start()
		elif sc == 'off':
			if self.rainbow:
				self.rainbow.runFlag = False
				self.rainbow = None
				self._pindata((0,0,0))
		elif sc == 'setsatlight':
			debug('setsatlight',data)
			sat = None
			light = None
			try:
				sl = data.split(',',1)
				if len(sl) > 1:
					(sat,light) = map(lambda n: int(n) if n.isnumeric() else None, sl)
				else:
					(sat,) = map(lambda n: int(n) if n.isnumeric() else None, sl)
				if(self.rainbow):
					self.rainbow._setSatLight(sat,light)
				debug(f'setsatlight: sat,light: {sat},{light}')
			except Exception as e:
				log(f'Exception {e}')
				pass

	def On(self):
		if self.rainbow:
			self.rainbow.runFlag = False
			self.rainbow = None
		self._writer({'rgb': [255,255,255]})

	def Off(self):
		if self.rainbow:
			self.rainbow.runFlag = False
			self.rainbow = None
		self._writer({'rgb': [0,0,0]})

	def _reader(self):
		if self.senfsPath:
			self._export()
		return self.data

	def _export(self):
		dataToFs(self.senfsPath,self.name,self.data)

if __name__ == "__main__":
	def monitor(sen):
		'''
		This function runs when invoked as python -l rgbsens and should be started
		as a service by systemd. Monitor, as it's name suggests, monitors a FIFO and
		reads lines containing r,g,b strings and uses to values to send to sen.write to
		be handled by the rgbLED class for hardware manipulation.
		Two methods are used on this interface. The first is a simple string
		of comma-separated rgb values, e.g.: 34,20,90, or
		using commands such as @off, @on. There are other commands defined and handled in
		the sensor object's doCommand method.
		'''
		def signalHandler(sig,frame):
			if sen.rainbow:
				sen.rainbow.runFlag = False
				print("Waiting on rainbow thread..")
				sen.rainbow.join()
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

		log(f"rgbMonitorDaemon - {sen.data['modinfo']} pid {os.getpid()}")
		try:	
			if os.path.exists(sen.monitorPath):
				os.unlink(sen.monitorPath)
			os.mkfifo(sen.monitorPath,mode=0o666)
			os.chmod(sen.monitorPath,0o666)
		except Exception as e:
			log(f'{e} Creating fifo on {sen.monitorPath}')
			return
		while True:
			with open(sen.monitorPath) as f:
				line = str(f.read().strip().split('\n')[0])
				debug(f'line {line}')
				if line.startswith('@cmd'):
					tag, line = line.split(':',1)
					if ':' in line:
						command, data = line.split(':',1)
					else:
						command = line
						data = None
					debug('Command',command,'Data',data)
					sen.doCommand(command,data)
					continue
				if len(line):
					try:
						r,g,b = map(int,line.split(',',2))
						data = {'rgb': (r,g,b)}
						sen.write(data)
					except Exception as e:
						log(f'monitor exception {e}')
						continue
			time.sleep(.1)
	parser = argparse.ArgumentParser(description="Sensor and Daemon for RGB Widget")
	parser.add_argument('-d','--debug',action='store_true', default=False)
	parser.add_argument('-l','--logfile',type=str, metavar='logfile', default=logfile)
	args = parser.parse_args()
	debugEnabled = args.debug
	if args.logfile:
		logfile = args.logfile
	sen = rgbLED('rgb',rgbPins,senfs=f'/sensor')
	monitor(sen)
```