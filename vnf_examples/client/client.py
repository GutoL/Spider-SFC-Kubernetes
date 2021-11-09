import requests
from kubernetes import client, config

def get_vnf_service_ip(service_name):
    config.load_kube_config() # running outside pod
    #config.load_incluster_config() # running inside pod

    v1 = client.CoreV1Api()
    
    services = v1.list_service_for_all_namespaces(watch=False)
    for svc in services.items:
        if service_name == str(svc.metadata.name):
            return svc.spec.cluster_ip

files = {
    'file': ('image.jpg', open('image.jpg', 'rb')),
}

first_vnf_service_name = 'my-sfc-compress-image-service'
url = get_vnf_service_ip(first_vnf_service_name)
url = 'http://'+str(url)+':5000'

response = requests.post(url, files=files)
print(response.content)
