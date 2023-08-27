# 
# Utility functions for sensor filesystems
#
import os

def dataToFs(basepath,name, data):
	'''
	Recursively create data nodes in sensorfs
	basepath: e.g, /sensor
	name: system name, e.g, pi4
 	data: dict of data
	each element would be in /sensor/data/pi4/element
	'''
	basepath = os.path.join(basepath,name)
	for k,v in data.items():
		if type(v) is dict:
			dataToFs(basepath,k,v)
		else:
			if not os.path.exists(basepath):
				os.makedirs(basepath,exist_ok=True)
			fn = os.path.join(basepath,k)
			with open(fn,'w') as f:
				f.write(f'{v}\n')
