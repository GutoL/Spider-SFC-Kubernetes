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

    @route('/sfc', methods=['POST'])
    def create_sfc(self)-> str:
        request_json = request.json

        # 1 - get status of infrastructure from collector.py
        response = requests.get(self.config['monitor_ip'])
        graph_json = response.json()

        headers = {'Content-type': 'application/json'}

        for vnf in request_json['VNFs']:
            data = {"graph": graph_json, "vnf":vnf}
            requests.post(self.config['agent_ip']+'placement',data=data, headers=headers)
        

        # 2 - call the agent to create the SFC request
        # 3 - send the SFC request to the environment controller (main.py)

        return ''


app = Flask(__name__)
Orchestrator.register(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4100, debug=True)
