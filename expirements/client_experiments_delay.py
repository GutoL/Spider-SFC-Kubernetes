import json
import requests
import time
import numpy as np
import time
from kubernetes import client, config

def get_vnfs_runtimes(data):
    positions = [ind for ind, ch in enumerate(data) if ch.lower() == '"']
    positions.append(len(data))
    
    vnfs_runtimes = {}

    for i in range(len(positions)-1):
        substring = data[positions[i]: positions[i+1]].replace('\\','').replace('"','')
        
        for x in substring.split('->'):
            if len(x) == 0:
                continue
            runtime = x.split('=')

            if runtime[0].strip() not in vnfs_runtimes:
                vnfs_runtimes[runtime[0].strip()] = [runtime[1].strip()]
            else:
                vnfs_runtimes[runtime[0].strip()].append(runtime[1].strip())
    
    return vnfs_runtimes


def get_vnf_service_ip(service_name):
    config.load_kube_config() # running outside pod
    #config.load_incluster_config() # running inside pod

    v1 = client.CoreV1Api()
    
    services = v1.list_service_for_all_namespaces(watch=False)
    for svc in services.items:
        if service_name == str(svc.metadata.name):
            return svc.spec.cluster_ip

def call_sfc(service_name, image_name='image.jpg'):

    files = {
        'file': ('image.jpg', open(image_name, 'rb')),
    }

    vnf_port = 5000

    url = get_vnf_service_ip(service_name)
    url = 'http://'+str(url)+':'+str(vnf_port)

    start = time.time()
    response = requests.post(url, files=files)
    end = time.time()

    vnfs_runtimes = get_vnfs_runtimes(response.content)
    return float(end-start), vnfs_runtimes


api_url = 'http://192.168.0.209:3500/sfc_request'
sfc_name = 'my-sfc'
first_vnf_service_name = 'my-sfc-compress-image-service'

number_of_vnfs = 3

f = open('sfc_requests_examples/sfc_request_example_'+str(number_of_vnfs)+'_vnfs.json')
request_data = json.load(f)
f.close()

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

number_of_experiments = 30
times_list = []
result = ''

wait_time = 8

for x in range(number_of_experiments):
    print('Starting:',x)
    
    # creating the SFC
    r = requests.post(api_url, data=json.dumps(request_data), headers=headers)  
    
    time.sleep(wait_time)
    time_elapsed, vnfs_runtimes = call_sfc(first_vnf_service_name, 'spider-face.jpg')
    times_list.append(time_elapsed)

    result += str(time_elapsed)+'\n'

    for vnf in vnfs_runtimes:
        result += vnf+':'+vnfs_runtimes[vnf][0]+','+vnfs_runtimes[vnf][1]+'\n'

    r = requests.delete(api_url+'/'+sfc_name)
    time.sleep(wait_time)

print('Mean placement time (seconds):',np.mean(times_list))
print('Standard deviation placement time:', np.std(times_list))

f = open("results/delay_results_"+str(number_of_vnfs)+"_vnfs.txt", "w")
f.write(result)
f.write('Mean placement time (seconds): '+str(np.mean(times_list))+'\n')
f.write('Standard deviation placement time: '+str(np.std(times_list)))
f.close()
