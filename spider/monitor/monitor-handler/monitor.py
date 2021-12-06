from flask import Flask
from flask_classful import FlaskView, route #, request
import json
import requests

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
            r = requests.get(machine['ip']+':'+str(machine['port']))
            r = r.json()
            response['nodes'].append(r['node'])

            for l in r['links']:
                response['edges'].append(l)
        
        return response

if __name__ == '__main__':
    app = Flask(__name__)
    Monitor.register(app)
    app.run(host='0.0.0.0', port=4997, debug=True)

