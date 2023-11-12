#
# RestAPI Server
#
```python
import requests
import json

def get_sen(server,host,sensor):
    headers = {'Accept': 'application/json'}
    url = f'http://{server}:4242/read?host={host}&sensor={sensor}'
    r = requests.get(url=url, headers=headers)
    #print(f'DEBUG: {url} response is {r}')
    #return {}
    try:
        js = r.json()
    except Exception as e:
        #print('Error in JSON response')
        return None
    if type(js) is str:
        try:
            d = json.loads(js)
            return d
        except Exception as e:
            #print(f'JSON String: {js}, error: {e}')
            return None
    return r.json()

def get_list(server,host):
    headers = {'Accept': 'application/json'}
    url = f'http://{server}:4242/list?host={host}'
    r = requests.get(url=url, headers=headers)
    #print(f'DEBUG: {url} response is {r}')
    #return {}
    try:
        js = r.json()
    except Exception as e:
        #print('Error in JSON response')
        return None
    if type(js) is str:
        try:
            d = json.loads(js)
            return d
        except Exception as e:
            #print(f'JSON String: {js}, error: {e}')
            return None
    return r.json()


def get_hosts(server):
    headers = {'Accept': 'application/json'}
    url = f'http://{server}:4242/hosts'
    r = requests.get(url=url, headers=headers)
    #print(f'DEBUG: {url} response is {r}')
    #return {}
    try:
        js = r.json()
    except Exception as e:
        #print('Error in JSON response')
        return None
    if type(js) is str:
        try:
            d = json.loads(js)
            return d
        except Exception as e:
            #print(f'JSON String: {js}, error: {e}')
            return None
    return r.json()
```
