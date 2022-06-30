from flask import Flask
from flask_classful import FlaskView, route, request
import json
import requests
from flask_cors import CORS

class Monitor(FlaskView):
    
    route_base = '/'
    def __init__(self):
        f = open('config.json')
        self.config = json.load(f)
        f.close()

    @route('/data', methods=['GET'])
    def get_data(self):
        response = {"nodes":[],"edges":[]}
        
        for machine in self.config['machines']:
            try:
                r = requests.get(machine['ip']+':'+str(machine['port']))
                r = r.json()
                response['nodes'].append(r['node'])

                for l in r['links']:
                    response['edges'].append(l)
            except Exception as e:
                print(e)
        
        return response

    @route('/sfc_request', methods=['POST'])
    def create_sfc(self)-> str:
        request_json = request.json

        sfc_info = {'name':request_json['name'].lower().replace(' ','-'),
                    'source':request_json['source'],
                    'destination':request_json['destination'],
                    'requirements':request_json['requirements']
                    }

        
        graph_json = self.get_data()

        data = {
                'graph': graph_json, 
                'vnfs':request_json['VNFs'],
                'flow_entries':request_json['flow_entries'], 
                'sfc_info':sfc_info
                }

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.post(self.config['agent_ip']+'sfc_request', json=data, headers=headers)
        return response

if __name__ == '__main__':
    app = Flask(__name__)
    CORS(app)
    Monitor.register(app)
    app.run(host='0.0.0.0', port=4997, debug=True)

