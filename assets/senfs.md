# Export dictionary to /sensor/*<host>/<sensortype>/<members>*

```python
import os
import time
import sensor

class senfs(sensor.Sensor):
	'''
	sensor class to read sensor data from sensorfs
	'''
	def __init__(self, stype, host):
		'''
		senfs(stype, host)
		stype is sensor type like 'aht10' or 'bmp280''
		host: sensor's host
		'''
		super().__init__(type,self._reader)
		self.type = stype
		self.host = host
		self.read()

	def _reader(self):
		'''
		_reader reads and returns data. Saves current data in super().data
		Don't call directly, use read()
		'''
		path = os.path.join('/sensor',self.host,self.type,f'{self.type}.json')
		with open(path) as f:
			self.data = json.load(f)
		return self.data;
```