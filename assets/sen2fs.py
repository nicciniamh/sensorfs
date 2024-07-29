import os
import json

def dataToFs(basepath,dataclass,data):
	'''
	Recursively create data nodes in sensorfs
	basepath: e.g, /sensor
	name: system name, e.g, pi4
	data: dict of data
	each element would be in /sensor/host/dataclass/element
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
