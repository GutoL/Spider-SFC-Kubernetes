from flask import Flask
from flask_classful import FlaskView, route, request
import os
import tarfile
import json
import requests
from utils import Utils
from flask_cors import CORS


class EnvironmentController(FlaskView):
    route_base = '/'

    # On the init method, we load the system configuration from the config file
    def __init__(self):
        f = open('system.config')
        self.config = json.load(f)
        f.close()

    def index(self):
        return "Environment controller is working"
    
    def _create_compressed_dockerfile(self, vnf_files_path, file_name):
        try:
            tar = tarfile.open(file_name, "w:gz")
            filenames = os.listdir(vnf_files_path+'/')
            
            for filename in filenames:
                tar.add(vnf_files_path+filename, arcname=filename)
            tar.close()
            return True
        except:
            return False

    def _create_docker_image(self, image_name, next_vnf, last_vnf, vnf_files_path, node_name):

        vnf_json_config = {"next_vnf": next_vnf, "last_vnf": last_vnf, "port":self.config['vnf_port']}

        with open(vnf_files_path+'/config_vnf.json', 'w', encoding='utf-8') as f:
            json.dump(vnf_json_config, f, ensure_ascii=False, indent=4)

        if self._create_compressed_dockerfile(vnf_files_path, self.config['dockerfile_name']):
            # url = self.config['docker_url']+"build?t="+image_name
            r = requests.get(self.config['k8s_url']+'/api/v1/nodes/'+node_name)

            url_node = r.json()

            ip_info = url_node['status']['addresses']

            for ip in ip_info:
                if 'ip' in ip['type'].lower():
                    url = ip['address']
                    break

            url += ':5555/build?t='+image_name
            # url = 'http://'+url_node['metadata']['annotations']['flannel.alpha.coreos.com/public-ip']+':5555/build?t='+image_name

            command = 'curl -v -X POST -H "Content-Type:application/tar" --data-binary'+" '@"+self.config['dockerfile_name']+"' "+url
            
            os.system(command) # we used the os.system command because we couldn't use the requests library to send the tar.gz file via post to the docker ¯\_(ツ)_/¯
            os.remove(self.config['dockerfile_name']) # '''

    def _create_k8s_deployment(self, vnf_name, node_name, replicas, resources):
        # curl --request POST --url http://localhost:8080/apis/apps/v1/namespaces/default/deployments --header 'content-type: application/json' --data '@deployment.json'
        
        headers = {'Content-type': 'application/json'}

        json_content = Utils.create_deployment_json(vnf_name, node_name, replicas, resources)
        r = requests.post(url=self.config['k8s_url_deployments'], data=json_content, headers=headers)
        #print(r.json())

        json_content = Utils.create_service_json_format(vnf_name+'-service', vnf_name)
        r = requests.post(url=self.config['k8s_url_services'], data=json_content, headers=headers)

    @route('/sfc_request', methods=['POST'])
    def sfc(self)-> str:
        
        sfc_json = request.json
        
        for i, vnf in enumerate(sfc_json['VNFs']):
            final_vnf_name = sfc_json['name']+'-'+vnf['name']
            node_name = vnf['node_name']
            
            if i == len(sfc_json['VNFs'])-1:
                last_vnf = True
                next_vnf = sfc_json['name']+'-destination'
            else:
                last_vnf = False
                next_vnf = sfc_json['name']+'-'+sfc_json['VNFs'][i+1]['name']+'-service'       

            # print('vnf:', final_vnf_name, 'last vnf:', last_vnf)

            self._create_docker_image(final_vnf_name, next_vnf, last_vnf, 
                                    self.config['vnfs_path']+vnf['name']+'/',node_name)
            self._create_k8s_deployment(final_vnf_name, vnf['node_name'], vnf['replicas'], vnf['resources'])

        return "ok\n"

if __name__ == '__main__':
    app = Flask(__name__)
    CORS(app)
    EnvironmentController.register(app)
    app.run(host="0.0.0.0", port=4900, debug=True)
    # ec = EnvironmentController()
    # ec._create_docker_image(image_name = 'sfc1_teste', files_path = '/home/guto/Desktop/vnf1/')
    

