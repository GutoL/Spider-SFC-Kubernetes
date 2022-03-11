import json
import requests
import time
import numpy as np
import time
import random

api_url = 'http://192.168.0.209:3500/sfc_request'
sfc_name = 'my-sfc'

number_of_vnfs = 2

f = open('sfc_requests_examples/sfc_request_example_'+str(number_of_vnfs)+'_vnfs.json')
request_data = json.load(f)
f.close()

machines = [
	'aerys-targaryen',
        'daenerys-targaryen',
	'ned-stark',
	'sansa-stark',
	'tyrion-lannister',
	'cersei-lannister'
	]

request_data['source'] = random.choice(machines)
request_data['destination'] = random.choice(machines)

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

number_of_experiments = 30
times_list = []
result = ''

for x in range(number_of_experiments):
	print('Starting:',str(x+1)+'/'+str(number_of_experiments))
	# creating the SFC
	try:
		start = time.time()
		r = requests.post(api_url, data=json.dumps(request_data), headers=headers)
		end = time.time()

		times_list.append(end-start)
		result += str(end-start)+'\n'

		r = requests.delete(api_url+'/'+sfc_name)
		time.sleep(5)
	except:
		print('Error!')

print('Mean placement time (seconds):',np.mean(times_list))
print('Standard deviation placement time:', np.std(times_list))

f = open("results/placement_results_"+str(number_of_vnfs)+"_vnfs.txt", "w")
f.write(result)
f.write('Mean placement time (seconds): '+str(np.mean(times_list))+'\n')
f.write('Standard deviation placement time: '+str(np.std(times_list)))
f.close()
