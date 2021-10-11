from flask import Flask
from flask_classful import FlaskView #, route, request
import json
import requests

class Monitor(FlaskView):
    
    route_base = '/'
    def __init__(self):
        f = open('config.json')
        self.config = json.load(f)
        f.close()

    def index(self):
        response = {"nodes":[],"links":[]}
        
        for machine in self.config['machines']:
            r = requests.get(machine['ip']+':'+str(machine['port']))
            r = r.json()
            response['nodes'].append(r)
        
        headers = {'Content-type': 'application/json'}
        for link in self.config['links']:
            url = link['source']['ip']+':'+str(link['port'])+'/link_consumption'
            data = json.dumps({"interface":link["interface"]}, indent=4)
            
            r = requests.post(url=url, data=data, headers=headers)
            r = r.content.decode('utf8')
            response['links'].append({"interface":link["interface"], "consumption":r})
        
        return json.dumps(response)+'\n'

if __name__ == '__main__':
    app = Flask(__name__)
    Monitor.register(app)
    app.run(host='0.0.0.0', port=5000)

