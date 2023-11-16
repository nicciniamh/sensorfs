#!/usr/bin/env python3
import os
import sys
import time
import json
import argparse
import importlib
import _thread
sys.path.append(os.path.expanduser('~/lib'))
import debuglog
import asyncio
import i2cdev
from collectconf import fssens, i2csens
from sensorfs import dataToFs

hostname = os.uname()[1].split('.')[0]

log = None
debug = None

async def collector(sensor,hostname):
	while True:
		try:
			debug(f'Reading {sensor.name}')
			data = sensor.read()
			path = os.path.join('/sensor',hostname,sensor.name)
			dataToFs(path,sensor.name,data)
		except:
			data = False
		await asyncio.sleep(1)

async def main():
	global log
	global debug
	global i2csens
	global fssens
	dbg = False
	logfile = False
	sensors = {}
	parser = argparse.ArgumentParser(description="collect sensor data and export to sensorfs")
	parser.add_argument('-l','--logfile',type=str, metavar='logfile', default=logfile)
	parser.add_argument('-d','--debug',action='store_true', default=dbg, help='Enable debug message')
	args = parser.parse_args()
	if args.logfile == False:
		log = debuglog.Logger('/dev/null')
		log.setStdio(True)
	else:
		log = debuglog.Logger(os.path.expanduser(args.logfile))
	debug = debuglog.Debug(args.debug,log)
	for name,module in fssens.items():
		debug(f"Creating fs sensor for {name}")
		try:
			m = importlib.import_module(module)
			sensors[name] = m.sensor()
		except Exception as e:
			log(f'Failure creating fssen/{name} from module {module}')

	for sid,config in i2csens.items():
		debug(f"Creating i2c sensor {config['name']}@{hex(config['address'])}")
		s = i2cdev.i2cdev(devaddr=config['address'],name=config['name'])
		if not s:
			log(f"Could not get a sensor object for {config['name']}@{hex(config['address'])}")
		else:
			s.name = config['name']
			sensors[sid] = s

	tasks = [asyncio.create_task(collector(sensor,hostname)) for name,sensor in sensors.items()]
	await asyncio.gather(*tasks)

if __name__ == "__main__":
	if True:
		asyncio.run(main())
