import json
import requests
import time

api_url = 'http://192.168.0.209:3500/sfc_request'

number_of_vnfs = 3

f = open('sfc_requests_examples/sfc_request_example_'+str(number_of_vnfs)+'_vnfs.json')
request_data = json.load(f)
f.close()

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

r = requests.post(api_url, data=json.dumps(request_data), headers=headers)
