from flask import Flask
from vnf_interface import VNF
import json

# https://github.com/Naklecha/firewall

class Firewall(VNF):
    def _process_data(self, request):

        ip_client = request.environ['REMOTE_ADDR']
        port_client = request.environ['REMOTE_PORT']
        
        f = open('firewallrules.json',)
        config = json.load(f)

        if ip_client in config['ListOfBannedIpAddr']:
            return None

        if port_client in config['ListOfBannedPorts']:
            return None

        prefix = ip_client.split('.')[0]
        
        if prefix+'.' in config['ListOfBannedPrefixes']:
            return None

        return request.json


if __name__ == '__main__':
    app = Flask(__name__)
    
    my_vnf = Firewall(vnf_config_file='config_vnf.json')
    my_vnf.register(app)
    app.run(host="0.0.0.0", port=5000, debug=True)