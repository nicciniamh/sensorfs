import time
from sensor import Sensor
from dflib.pi5therm import Fan, FanSpeed
from dflib.debug import debug, set_debug

class sensor(Sensor):
	"""
	Basic sensorfs module for fan control
	"""
	def __init__(self):
		super().__init__('cpu_fan',self._reader,self._writer)
		self.data = {}
		self._fan = Fan()
		self.monitorPath = '/tmp/cpu_fan.fifo'

	def _reader(self):
		self.data = {
			'description': 'cpu fan control',
			'modinfo': 'com.ducksfeet:vsen:cpu_fan:v0.1',
			'temp': self._fan.cpu_temp.temperature,
			'speed': str(self._fan.speed),
			'rpm': int(self._fan.rpm),
			'time': int(time.time())
		}
		return self.data

	def _writer(self,data):
		if not type(data) is int:
			raise ValueError('data must be integer')
		data = FanSpeed(data)
		self._fan.set_speed(data)
		self._reader()
		return self.data
