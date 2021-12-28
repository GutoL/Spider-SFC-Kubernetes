from kubernetes import client, config
import requests
import json
import abc

from flask import Flask
from flask_classful import FlaskView, route, request


class VNF(FlaskView, metaclass=abc.ABCMeta):

    route_base = '/'

    def __init__(self, vnf_config_file='config_vnf.json'):
        fp = open(vnf_config_file)
        vnf_config = json.load(fp)
        self.vnf_config = vnf_config
    
    @route('/', methods=['POST', 'GET'])
    def index(self) -> str:
        processed_data = self._process_data(request)
        
        if processed_data == None:
            return 'Error! Flow blocked...'

        try:
            response = self._forward_data(processed_data)
            response += '\nOK'

        except:
            if self.vnf_config['last_vnf']:
                response = 'OK last vnf'
            else:
                response = 'Error!'

        # print(processed_data['data'])
        return response

    @abc.abstractmethod
    def _process_data(self, request):
        return request

    def _get_service_ip(self,service_name):
        # config.load_kube_config() # running outside pod
        config.load_incluster_config() # running inside pod

        v1 = client.CoreV1Api()
        
        services = v1.list_service_for_all_namespaces(watch=False)
        for svc in services.items:
            if service_name == str(svc.metadata.name):
                return svc.spec.cluster_ip
    
    def _forward_data(self, data):
        next_vnf = self.vnf_config['next_vnf']
        next_vnf = self._get_service_ip(next_vnf)

        port = self.vnf_config['port']

        url = 'http://'+str(next_vnf)+':'+str(port)+'/'

        headers = {'Content-type': 'application/json'}

        r = requests.post(url=url, json=data, headers=headers)
        
        data = json.dumps(r.text) # r.json()
        
        return data

class MyVNF(VNF):
    def _process_data(self, data):
        return request.json

if __name__ == '__main__':
    app = Flask(__name__)
    
    my_vnf = MyVNF(vnf_config_file='config_vnf.json')
    my_vnf.register(app)
    app.run(host="0.0.0.0", port=5000)
