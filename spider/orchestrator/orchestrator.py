from flask import Flask
from flask_classful import FlaskView, route, request
import requests
import json

class Orchestrator(FlaskView):
    route_base = '/'

    # On the init method, we load the system configuration from the config file
    def __init__(self):
        f = open('system.config')
        self.config = json.load(f)
        f.close()

    @route('/sfc_request', methods=['POST'])
    def create_sfc(self)-> str:
        request_json = request.json

        print('request_json',request_json['flow_entries'])
        
        sfc_info = {'name':request_json['name'].lower().replace(' ','-'),
                    'source':request_json['source'],
                    'destination':request_json['destination'],
                    'requirements':request_json['requirements']
                    }

        
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        # 1 - get status of infrastructure from monitor.py
        response = requests.get(self.config['monitor_ip']+'/data')
        graph_json = response.json()

        data = {
                'graph': graph_json, 
                'vnfs':request_json['VNFs'],
                'flow_entries':request_json['flow_entries'], 
                'sfc_info':sfc_info
                }

        print('source',sfc_info['source'],'destination',sfc_info['destination'])

        # 2 - call the agent to create the SFC request
        response = requests.post(self.config['agent_ip']+'placement',json=data, headers=headers)
        
        # print(response.json())
        
        # 3 - send the SFC request to the environment controller (main.py)
        requests.post(self.config['environment_controller_ip']+'sfc_request',json=response.json(), headers=headers) # '''
        print('Placement done!')

        return ''


app = Flask(__name__)
Orchestrator.register(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4996, debug=True)
