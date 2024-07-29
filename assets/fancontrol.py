#!/usr/share/pyenv/bin/python3
"""
Rest server to control CPU fan on Raspberry Pi 5
"""
import aiohttp
import aiohttp.web
import argparse
import asyncio
import json
import sys
import os

sys.path.append(os.path.expanduser('~nicci/lib'))

from dflib.debug import debug, set_debug
import cpuinfo
import cpufan


sens = {
'cpu_info': cpuinfo.sensor(),
'cpu_fan': cpufan.sensor()
}

async def read(request):
	global sens
	sensor = request.query.get('sensor','cpu_fan')
	if not sensor in sens:
		debug("invalid sensor")
		body = {"error": "invalid sensor ({sensor})"}
	else:
		debug('sensor',sensor)
		body = sens[sensor].read()
	return aiohttp.web.Response(body=json.dumps(body),headers = {'Content-Type': 'text/json'})

async def write(request):
	global sens
	body = None
	sensor = request.query.get('sensor','cpu_fan')
	value = request.query.get('value',None)
	if not value:
		body = {'error': 'value must be specified'}
	try:
		value = int(value)
	except:
		body = {'error': 'Invalid value'}

	if not body:
		if not sensor in sens:
			debug("invalid sensor")
			body = {"error": "invalid sensor ({sensor})"}
		else:
			try:
				body = sens[sensor].write(value)
			except Exception as e:
				body = {'sensor exception': str(e)}
	return aiohttp.web.Response(body=json.dumps(body),headers = {'Content-Type': 'text/json'})

async def main():
	app = aiohttp.web.Application()
	# Define routes
	app.router.add_get('/read', read)
	app.router.add_get('/write', write)

	# Run the app
	runner = aiohttp.web.AppRunner(app)
	await runner.setup()
	site = aiohttp.web.TCPSite(runner, port=4243)
	debug(f"fan control {runner}:{site}")
	await site.start()
	while True:
		await asyncio.sleep(3600)  # Sleep for 1 hour

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Story Server")
	parser.add_argument('-d','--debug',action='store_true',default=False)
	args = parser.parse_args()
	set_debug(args.debug)
	asyncio.run(main())
