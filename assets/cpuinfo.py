#!/usr/bin/env python
import time
import sensor
import psutil
import _thread

class sensor(sensor.Sensor):
	def __init__(self,*args):
		super().__init__('cpu_usage',self._reader)
		self._data = {'usage': 0.0, 'boot_time': 0, 'loadavg': (0,0,0), 'cputemp': 0.0, 'vmem': 0, 'modinfo': 'cpu_usage:com.ducksfeet:v0.2', 'name': 'cpuinfo'}
		for i in range(0,4):
			self._data[f'core{i}'] = 0.0

		_thread.start_new_thread(self.collector,())

	def collector(self):
		'''
		collector runs in a thread to collect slow data in background 
		and the reader method can return without blocking
		'''
		while True:
			with open('/sys/class/thermal/thermal_zone0/temp') as f:
				cputemp=float(f.read().strip())/1000;

			with open('/proc/uptime', 'r') as f:
				boot_time = float(f.readline().split()[0])

			usage = psutil.cpu_percent(interval=.75)
			cores = psutil.cpu_percent(interval=0,percpu=True)
			for i in range(0,len(cores)):
				self._data[f'core{i}'] = cores[i]
			self._data['usage'] = usage
			self._data['loadavg'] = psutil.getloadavg()
			self._data['vmem'] = psutil.virtual_memory().percent
			self._data['cputemp'] = cputemp
			self._data['name'] = 'cpuinfo'
			self._data['modinfo'] = 'com.ducksfeet:vsen:cpuinfo:v0.3'
			self._data['boot_time'] = boot_time


	def _reader(self):
		return self._data
