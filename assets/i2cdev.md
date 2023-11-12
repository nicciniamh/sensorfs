# Example of hardware sensors accessed through Linux sysfs. 

[Sensor](sensor.html) Derived class for I2C Sensors

With this class we can create sensors on the I2C bus using their address or device path. 

The recognized sensors are

* Bosch *BMP280*
* Silicon Labs *Si7020*
* AOSONG *AHT10/AHT20* series

These are sensors who have a kernel module and their data exposed in /sysfs. The purpose of this sensor is to provide a consistent method of accessing the sensors in human readable units. 

  
```python

import os
import glob
import importlib
from sensor import Sensor
import time

''' 
Module for finding and instanciating I2C sensors that are defined in 
sysfs. This means they must be defined in /boot/config.txt and the 
appropriat kernel module loaded.

'''

I2C_BMP280 = 0x77
I2C_SI7020 = 0x40
I2C_AHT10 = 0x38


def _modver(component=""):
	return f"com.ducksfeet:i2cdev:{component}:v0.5"

class i2cdevException(Exception):
	pass

def _argFromDict(d,a,default=None):
	for k,v in d.items():
		if k == a:
			return v
	return default

class i2cdev(Sensor):
	def __init__(self,*args,**kwargs):
		defaults = {
			'aht10': {'address': I2C_AHT10, 'reader': self._read_aht},
			'bmp280': {'address': I2C_BMP280,'reader': self._read_bmp},
			'si7020': {'address': I2C_SI7020,'reader': self._read_si}
		}
		self.devpath = _argFromDict(kwargs,'devpath',None)
		self.devaddr = _argFromDict(kwargs,'devaddr',None)
		self.devtype = _argFromDict(kwargs,'devtype',None)
		if not self.devtype:
			if self.devaddr:
				self.devpath = get_i2c_device_node(self.devaddr)

			if not self.devpath or not self.devaddr:
				raise i2cdevException('No device type, address or path specified')
			elif self.devaddr:
				if not self.devpath:
					self.devpath = get_i2c_device_node(self.devaddr)
				node = os.path.join(self.devpath,'of_node/name')
				if os.path.exists(node):
					with open(node) as f:
						self.devtype = f.read().strip().strip('\x00')
			else:
				if not self.devpath:
					self.devpath = get_i2c_device_node(defaults[self.devtype])
					if not self.devpath:
						raise i2cdevException(f'Cannot find sensor profile for {self.devtype}')
		else:
			self.devpath = get_i2c_device_node(defaults[self.devtype]['address'])
			if not self.devpath:
				raise i2cdevException(f'Cannot find sensor profile for {self.devtype}')

		if not self.devtype:
			raise i2cdevException(f'Cannot find sensor profile for {self.devtype}')
		name = _argFromDict(kwargs,'name',self.devtype)
		self.devinfo = _modver(self.devtype)
		self._r = defaults[self.devtype]['reader']
		super().__init__(name,reader=self._reader)


	def _reader(self):
		self._r()
		for k in ['temp','tempc','pressure','humidity']:
			if k in self.data.keys():
				setattr(self,k,self.data[k])
		return self.data

	def _read_aht(self):
		def pathdata(path):
			with open(path) as f:
				n = float(f.read())
				return n / 1000.0
		tempc=pathdata(f'{self.devpath}/temp1_input')
		hum=pathdata(f'{self.devpath}/humidity1_input')
		self.data =  {
			'description': 'AOSONG AHT10/AHT20',
			'modinfo': self.devinfo,
			'tempc': tempc,
			'temp': ((tempc/5)*9)+32,
			'humidity': hum,
			'time':  int(time.time()),
		}
		return self.data

	def _read_bmp(self):
		def _getVal(subject,what):
			subject=f"in_{subject}"
			with open(os.path.join(self.devpath,f'{subject}_{what}')) as f:
				return float(f.read().strip())
		tempc = float(_getVal('temp','input'))/1000.0
		temp = ((tempc/5)*9)+32
		pressure = float(_getVal('pressure','input')*10.0)
		self.data = {
			'description': 'Bosch Sensortec BMP280',
			'pressure': pressure,
			'temp': temp,
			'tempc': tempc,
			'time': int(time.time()),
			'modinfo': self.devinfo,
		}
		return self.data

	def _read_si(self):
		def _getVal(subject,what):
			subject=f"in_{subject}"
			with open(os.path.join(self.devpath,f'{subject}_{what}')) as f:
				return float(f.read().strip())
		raw = _getVal('temp','raw')
		offset = _getVal('temp','offset')
		scale = _getVal('temp','scale')
		tempc = ((raw+offset)*scale/1000)
		temp =  ((tempc/5)*9)+32

		raw = _getVal('humidityrelative','raw')
		offset = _getVal('humidityrelative','offset')
		scale = _getVal('humidityrelative','scale')
		rh = ((raw+offset)*scale/1000)
		self.data = {
			'description': 'Silicon Labs Si7020',
			'temp': temp,
			'tempc': tempc,
			'humidity': rh,
			'time': int(time.time()),
			'modinfo': self.devinfo,
		}
		return self.data

def get_i2c_device_node(devaddr,bus=1):
	'''
	Parameters: devaddr: Required. The i2c address of the device.
				bus: the i2c bus number. Default is 1
	'''
	sn = f'/sys/class/i2c-adapter/i2c-{bus}/'
	try:
		dn = '{}-{:04X}'.format(bus,devaddr)
	except:
		print('wtf',bus,devaddr)
	if not os.path.exists(sn):
		return None
	devpath = os.path.join(sn,dn)
	if not os.path.exists(devpath):
		return None

	if os.path.exists(os.path.join(devpath,'hwmon')):
		# Device is in hwmon
		node = os.path.join(devpath,'hwmon')
		r = glob.glob(f'{node}/hwmon*')
		if len(r):
			return os.path.join(node,r[0])
		else:
			return None

	r = glob.glob(f'{devpath}/iio:device*')
	if not len(r):
		return None

	return os.path.join(devpath,r[0])

if __name__ == "__main__":
	import pprint
	def dumpi2cdata(d):
		dkeys = list(d.keys())
		dkeys.sort()
		nd = {i: d[i] for i in dkeys}
		for k,v in nd.items():
			v = d[k]
			if k == 'time':
				v = time.strftime('%D %T',time.localtime(v))
			if type(v) is float:
				v = '{:.2f}'.format(v)
			print(f"\t{k}={v}")
	for a in [0x38,0x77]:
		s = i2cdev(devaddr=a)
		if s:
			s.read()
			print(f"Sensor: {s.name}:")
			pprint.pp(s.__dict__)
		else:
			print(f'Failed to find I2C device at {hex(a)}')

```

---

<small>This page, images and code are Copyright &copy; 2023 [Nicole Stevens](/sensorfs/about.html) All rights reserved.</small>
