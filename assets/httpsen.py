import requests
import json

def get_sen(server,host,sensor):
	headers = {'Accept': 'application/json'}
	url = f'http://{server}:4242/read?host={host}&sensor={sensor}'
	r = requests.get(url=url, headers=headers)
	try:
		js = r.json()
	except Exception as e:
		return None
	if type(js) is str:
		try:
			d = json.loads(js)
			return d
		except Exception as e:
			return None
	return r.json()

def write_sen(server,host,sensor,data):
	headers = {'Accept': 'application/json'}
	url = f'http://{server}:4242/write?host={host}&sensor={sensor}&data={str(data)}'
	print(f'Requesting {url}')
	r = requests.get(url=url, headers=headers)
	try:
		js = r.json()
	except Exception as e:
		return None
	if type(js) is str:
		try:
			d = json.loads(js)
			return d
		except Exception as e:
			return None
	return r.json()

def get_list(server,host):
	headers = {'Accept': 'application/json'}
	url = f'http://{server}:4242/list?host={host}'
	r = requests.get(url=url, headers=headers)
	try:
		js = r.json()
	except Exception as e:
		return None
	if type(js) is str:
		try:
			d = json.loads(js)
			return d
		except Exception as e:
			return None
	return r.json()


def get_hosts(server):
	headers = {'Accept': 'application/json'}
	url = f'http://{server}:4242/hosts'
	r = requests.get(url=url, headers=headers)
	try:
		js = r.json()
	except Exception as e:
		return None
	if type(js) is str:
		try:
			d = json.loads(js)
			return d
		except Exception as e:
			return None
	return r.json()
