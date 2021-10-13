import psutil
from flask import Flask
from flask_classful import FlaskView, route, request
import sys

import copy
import json
import subprocess
import socket

class MonitorDaemon(FlaskView):
    def __init__(self):
        f = open('node_config.json')
        self.node_config = json.load(f)
        f.close()

    route_base = '/'

    def link_consumption(self, interface)-> str:
                
        # getting usage data for current monthly period and converting it to a string
        command = "vnstat -i "+str(interface)+" --oneline | cut -d ';' -f 7"

        output = subprocess.check_output(command, shell=True)
        output = output.decode('utf8').replace('\n','')
        return str(output)
        
    
    def _get_cpu_consumption(self):
        total_cpu = psutil.cpu_count(logical=False)
        cpu_used = (total_cpu*psutil.cpu_percent())/100
        return total_cpu - cpu_used # in cores
    
    def _get_total_cpu(self):
        return psutil.cpu_count(logical=False) # in cores
    
    def _get_memory_consumption(self):
        mem_available = psutil.virtual_memory().available
        return float(mem_available)/ (1024 * 1024 * 1024) # in GB

    def _get_total_memory(self):
        mem_total = psutil.virtual_memory().total
        return float(mem_total)/ (1024 * 1024 * 1024) # in GB

    def _get_storage_consumption(self, path='/'):
        return float(psutil.disk_usage(path).free)/ (1024 * 1024 * 1024) # in GB

    def _get_total_storage(self, path='/'):
        return float(psutil.disk_usage(path).total)/ (1024 * 1024 * 1024) # in GB

    def index(self):

        node_config = copy.deepcopy(self.node_config['node'])

        node_config['available_resources'] = {
            'cpu':self._get_cpu_consumption(),
            'memory':self._get_memory_consumption(),
            'storage': self._get_storage_consumption()
        }

        node_config['resources'] = {
            'cpu':self._get_total_cpu(),
            'memory':self._get_total_memory(),
            'storage': self._get_total_storage()
        }

        links_config = copy.deepcopy(self.node_config['links'])

        all_links = []

        for link in links_config:
            bandwidth = self.link_consumption(link['interface'])
            
            host_name = socket.gethostname()
            host_ip = 'http://'+socket.gethostbyname(host_name + '.local')
            
            port = link.pop('src_port')
            link['source'] = {'id':node_config['id'], 'ip':host_ip,'port':port}
            
            link['available_resources']['bandwidth'] = bandwidth
            all_links.append(link)

        return {"node": node_config, "links":all_links}


if __name__ == '__main__':
    app = Flask(__name__)
    MonitorDaemon.register(app)

    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 4000
        
    app.run(host='0.0.0.0', port=port)
