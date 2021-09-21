# from kubernetes import client, config
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
    
    @route('/', methods=['POST'])
    def index(self) -> str:
        content = request.json
        processed_data = self._process_data(content)

        try:
            self._forward_data(processed_data)
            response = 'OK'
        except:
            if self.vnf_config['last_vnf']:
                response = 'OK last vnf'
            else:
                response = 'Error!'

        return response

    @abc.abstractmethod
    def _process_data(self, data):
        return data

    def _forward_data(self, data):
        next_vnf = self.vnf_config['next_vnf']
        port = self.vnf_config['port']

        url = 'http://'+str(next_vnf)+':'+str(port)+'/'
        r = requests.post(url=url, data=data)
	data = json.dumps(r.text) # r.json()
        
        # return data

class MyVNF(VNF):
    def _process_data(self, data):
        return data

if __name__ == '__main__':
    app = Flask(__name__)
    
    my_vnf = MyVNF(vnf_config_file='config_vnf.json')
    my_vnf.register(app)
    app.run(host="0.0.0.0", port=5000)
