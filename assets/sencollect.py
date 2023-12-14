#!/usr/bin/env python3
'''
Improved sensor collector

This script reads a ini-file type config, default is ~/etc/collect.conf
which has sections for each sensor collected. There are two formats:

Virtual (or module) Sensors:
	[sensor]
	type=vsen
	enabled=[yes|no]
	module=name of importable python module
	interval=seconds between readings, float

i2c Sensors:
	[sensor]
	type=i2c
	enabled=[yes|no]
	name=name of sensor
	address=i2c address of sensor, either a decimal or hex number
	interval=seconds between readings, float


If an entry's enabled item is not set to yes the sensor will be ignored.

Once all the sensors are initialized an async 'task' called collector is created for each
where the sensor's data is read, exported to the filesystem and then sleep for interval 
seconds. The main task waits for all the others to end or be killed.  

'''
import os
import sys
import time
import json
import argparse
import importlib
import asyncio
from configparser import ConfigParser

sys.path.append(os.path.expanduser('~/lib'))
import debuglog
import i2cdev
from sensorfs import dataToFs

hostname = os.uname()[1].split('.')[0]

log = None
debug = None
args = None
config = None

async def collector(sensor,hostname,interval):
	global debug
	global log
	while True:
		try:
			debug(f'Reading {sensor.name}')
			data = sensor.read()
			path = os.path.join('/sensor',hostname,sensor.name)
			dataToFs(path,sensor.name,data)
		except Exception as e:
			log(f'Exception in collector, sen={sensor}: {e}\nExiting thread.')
		await asyncio.sleep(interval)

async def main():
	global log
	global debug
	tasks = []
	defconf = '~/etc/collect.conf';
	parser = argparse.ArgumentParser(description="collect sensor data and export to sensorfs")
	parser.add_argument('-c','--config', type=str, metavar='filename', default=defconf,help=f"configuration file default: {defconf}")
	parser.add_argument('-l','--logfile',type=str, metavar='logfile', default=False)
	parser.add_argument('-d','--debug',action='store_true', default=False, help='Enable debug message')
	args = parser.parse_args()
	if args.logfile == False:
		log = debuglog.Logger('/dev/null')
		log.setStdio(True)
	else:
		log = debuglog.Logger(os.path.expanduser(args.logfile))
	debug = debuglog.Debug(args.debug,log)

	config = ConfigParser()
	config.read(os.path.expanduser(args.config))
	debug(f"Reading config in {args.config}: {config.sections()}")
	'''
	Loop through each section of config and construct sensors.
	'''
	sensors = {}
	for name in config.sections():
		sen = False
		s = config[name]
		debug(f"Reading section {name}: {s}")
		if s['enabled'].lower() == 'yes':
			interval = int(s['interval'])
			if s['type'] == 'i2c':
				if type(s['address']) is int:
					address = s['address']
				else:
					if s['address'].startswith('0x'):
						address = int(s['address'],16)
					else:
						address = int(s['address'])
				debug(f"Creating i2c sensor {name}@{hex(address)}")
				sen = i2cdev.i2cdev(devaddr=address,name=name)
				if not sen:
					log(f"Failure createing i2c/{name}@{hex(address)}")
				else:
					sen.name = name
			elif s['type'] == 'vsen':
				try:
					module = s['module']
					debug(f'Creating vsen {name} from {module}')
					sen = importlib.import_module(module).sensor()
				except Exception as e:
					log(f'Failure creating fssen/{name} from module {module}')
			if sen:
				sen.name = name
				sen.interval = interval
				sensors[name] = sen
	tasks = [asyncio.create_task(collector(sen,hostname,sen.interval)) for name,sen in sensors.items()]
	await asyncio.gather(*tasks)

if __name__ == "__main__":
	asyncio.run(main())
