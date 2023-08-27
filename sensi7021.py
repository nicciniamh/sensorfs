import time 
import board
import adafruit_si7021
from sensor import Sensor

'''
sensi7021.sensor is subclassed from sensor. 
Since there is no way to write the sensor data 
there is no writer. The superclass write method will raise IO error 
if used. isWriteable will return false. 
'''

class sensor(Sensor):
	''' abstracted si7021 sensor on standard i2c bus'''
	def __init__(self,name):
		super().__init__(name,self.reader,None)
		self.si7021 = adafruit_si7021.SI7021(board.I2C())

	def reader(self):
		''' return a dictionary with the sensor data '''
		tempc = self.si7021.temperature
		time.sleep(.25)
		humi = self.si7021.relative_humidity
		time.sleep(.25)
		tempf = ((tempc/5)*9)+32
		return {
			'tempf': tempf,
			'tempc': tempc,
			'humidity': humi
		}

