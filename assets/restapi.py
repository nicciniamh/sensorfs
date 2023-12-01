#!/usr/bin/env python3
#
# Simple RESTfull API Serveer for SensorFS.
# This is old code but shows the functionality
#
import os
import glob
import json
import os
import time
import argparse

from flask import Flask, request, jsonify
from flask_cors import CORS

from waitress import serve
debugFlag = True

app = Flask(__name__)
CORS(app)

class Debug:
	def __init__(self,enabled, logger ):
		self.enabled = enabled
		self.logger = logger

	def setlogger(self,logger):
		self.logger = logger
		return self

	def __call__(self,*args):
		if self.enabled:
			if self.logger:
				tstr  = time.strftime('%D:%T')
				logger(tstr,"DEBUG:",*args)
			else:
				print("DEBUG:",*args)

	def enable(self):
		self.enabled = True

	def disble(self):
		self.enabled = False

class Logger:
	def __init__(self,logfile):
		self.logfile = logfile
		self.stdio = False

	def setStdio(self,flag):
		self.stdio = flag

	def __call__(self,*args):
		tstr  = time.strftime('%D:%T')
		if self.stdio:
			print(tstr,*args)
		else:
			with open(self.logfile,'a') as f:
				print(tstr,*args,file=f)

logger = Logger('/dev/tty')
logger.setStdio(True)
debug = Debug(debugFlag,logger)

def writeSen(data):
	host = data['host']
	sensor = data['sensor']
	bpath = f"/sensor/{host}"
	if not os.path.exists(bpath):
		debug("Cannot find",bpath);
		return {'error': 'no such host'}
	path = f"{bpath}/{sensor}/{sensor}/writer"
	try:
		with open(path,w) as f:
			f.write(f"{data['data']}")
		return data;
	except Exception as e:
		debug(f"Error {e}")
		return {'error': f'{e} encountered writing data'}



def readSen(data):
	host = data['host']
	sensor = data['sensor']
	bpath = f"/sensor/{host}"
	if not os.path.exists(bpath):
		debug("Cannot find",bpath);
		return {'error': 'no such host'}
	path = f'{bpath}/{sensor}/{sensor}.json'
	if not os.path.exists(path):
		debug("Cannot find",path)
		#return {'error': 'no such sensor'}
		return {'error': f'no such sensor {path}'}
	try:
	#if True:
		with open(path) as f:
			data = json.load(f)
		debug("read, return data is",data)
		return data;
	#else:
	except Exception as e:
		debug(f"Error {e}")
		return {'error': f'{e} encountered reading data'}


def listSen(data):
	host = data['host']
	path = f"/sensor/{host}"
	if not os.path.exists(path):
		return {'error': 'no such host'}
	if not os.path.exists(path):
		return {'error': 'no such host'}
	senlist = []
	for p in glob.glob(f'{path}/*'):
		senlist.append(os.path.basename(p))
	return senlist

def listHost(data):
	path = f"/sensor"
	if not os.path.exists(path):
		return {'error': 'no such path'}
	hostlist = []
	for p in glob.glob(f'{path}/*'):
		hostlist.append(os.path.basename(p))
	return hostlist

commands = {
	'read': readSen,
	'list': listSen,
	'hosts': listHost,
	'write': writeSen,
}

@app.route('/<string:command>', methods=['GET', 'POST'])
def handle_command(command):
	debug("Command in",command)
	if command in commands:
		if request.method == 'GET':
			data = request.args.to_dict()
		elif request.method == 'POST':
			debug('Post method: request',request)
			try:
					data = request.get_json()
					if type(data) is not dict:
						raise Exception("Did not get data as dict")
			except Exception as e:
				debug(f'{e} encountered reading post data')
				return f'{e} encountered reading post data', 500

		result = commands[command](data)
		response = jsonify(result)
		#response.headers['Access-Control-Allow-Origin'] = '*'
		return response, 200
	else:
		return "Command not found", 404

if __name__ == '__main__':
	'''
	Start the server based on arguments. 
	Defaults are: debug disabled
				  listen address = 0.0.0.0
				  port = 4242

	If debugging is enabled the server runs with messages printed and debug messages from code otherwise
	debugging mesages are turned off and the server is run using waitress.serve 
	'''
	parser = argparse.ArgumentParser(description="API Server for SensorFS")
	parser.add_argument('-listen',type=str,metavar="address:[port]", default=None, help='listen on addr:port')
	parser.add_argument('-port',type=int,metavar='port', default=4242, help='Set port (default 4242)')
	parser.add_argument('-debug',action='store_true',default=False,help="Enable debugging message")
	args = parser.parse_args()
	port = args.port
	if args.listen:
		parts = args.listen.split(':')
		listenadr = parts[0]
		if len(parts) > 1:
			port = int(parts[1])
	else:
		listenadr = '0.0.0.0'

	if args.debug:
		debug.enable()
		app.run(port=port, host=listenadr)
	else:
		debug.disble()
		serve(app,port=port, host=listenadr)
