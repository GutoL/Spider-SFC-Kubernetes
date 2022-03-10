from flask import Flask
from flask_classful import FlaskView, route, request
import os
import tarfile
import json
import requests
from utils import Utils
from flask_cors import CORS
from copy import deepcopy

from kubernetes import client, config
from kubernetes.client.rest import ApiException

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

        vnf_json_config = {"vnf_name":image_name, "next_vnf": next_vnf, "last_vnf": last_vnf, 
                            "port":self.config['vnf_port']}

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

    def _get_node_name_by_id(self, infra_info, node_id):
        node_name = False

        for node in infra_info['nodes']:
            if node['id'] == node_id:
                node_name = node['name']
                break

        return node_name

    @route('/sfc_request', methods=['POST'])
    def sfc(self)-> str:
        
        sfc_json = request.json

        vnfs_to_place_temp = [

            {
                'name':'source',
                'final_vnf_name':sfc_json['name']+'-source',
                'node_name': sfc_json['source'],
                'replicas': 1,
                'resources': {'cpu':1, 'memory':1, 'storage':1},
                'last_vnf': False
            }            
        ]

        
        update_next_vnf_source = True
        infra_info = sfc_json['graph']

        for i, vnf in enumerate(sfc_json['VNFs']):
            vnf_to_place = {}
            
            vnf_to_place['name'] = vnf['name']
            vnf_to_place['final_vnf_name'] = sfc_json['name']+'-'+vnf['name']

            if update_next_vnf_source:
                vnfs_to_place_temp[0]['next_vnf'] = vnf_to_place['final_vnf_name']+'-service'
                update_next_vnf_source = False

            vnf_to_place['node_name'] = self._get_node_name_by_id(infra_info, vnf['node_id']) #vnf['node_name']
            vnf_to_place['replicas'] = vnf['replicas']
            vnf_to_place['resources'] = vnf['resources']
            
            if i == len(sfc_json['VNFs'])-1:
                last_vnf = False # True
                next_vnf = sfc_json['name']+'-destination-service'
            else:
                last_vnf = False
                next_vnf = sfc_json['name']+'-'+sfc_json['VNFs'][i+1]['name']+'-service'

            # print('vnf:', final_vnf_name, 'last vnf:', last_vnf)

            vnf_to_place['last_vnf'] = last_vnf
            vnf_to_place['next_vnf'] = next_vnf

            vnfs_to_place_temp.append(vnf_to_place)

        vnfs_to_place = []
        
        for i, flow_entry in enumerate(sfc_json['flow_entries']):
            
            if i < len(vnfs_to_place_temp):
                vnfs_to_place.append(vnfs_to_place_temp[i])
                update_next_vnf = True
            
            if len(flow_entry['path']) > 1:
                vnf_to_place = {}

                for path in range(len(flow_entry['path'])-1):
                    node_to_place_proxy = self._get_node_name_by_id(infra_info, flow_entry['path'][path][1])
                    
                    if node_to_place_proxy:
                        vnf_to_place['name'] = 'spider-proxy'
                        vnf_to_place['final_vnf_name'] = sfc_json['name']+'-'+flow_entry['vnf_name']+'-'+vnf_to_place['name']+'-'+str(path)
                        
                        if update_next_vnf:
                            vnfs_to_place[i]['next_vnf'] = vnf_to_place['final_vnf_name']+'-service'
                            update_next_vnf = False

                        vnf_to_place['node_name'] = node_to_place_proxy
                        vnf_to_place['replicas'] = 1
                        vnf_to_place['resources'] = {'cpu':1, 'memory':1, 'storage':1}

                        vnf_to_place['last_vnf'] = False
                        
                        if path == len(flow_entry['path'])-2:
                            vnf_to_place['next_vnf'] = sfc_json['name']+'-'+sfc_json['flow_entries'][i]['vnf_name']+'-service'
                        else:    
                            vnf_to_place['next_vnf'] = sfc_json['name']+'-'+flow_entry['vnf_name']+'-'+vnf_to_place['name']+'-'+str(path+1)+'-service'
                        
                        vnfs_to_place.append(deepcopy(vnf_to_place))
                        
                    else:
                        return 'Error!!!'
        
        vnfs_to_place.append(
            {
                'name':'destination',
                'final_vnf_name':sfc_json['name']+'-destination',
                'node_name': sfc_json['destination'],
                'replicas': 1,
                'resources': {'cpu':1, 'memory':1, 'storage':1},
                'next_vnf': '',
                'last_vnf': True
            }
        )

        for vnf in vnfs_to_place:
            # print(vnf,'\n---------------------')
            self._create_docker_image(vnf['final_vnf_name'], vnf['next_vnf'], vnf['last_vnf'],
                                    self.config['vnfs_path']+vnf['name']+'/', vnf['node_name'])

            self._create_k8s_deployment(vnf['final_vnf_name'], vnf['node_name'], vnf['replicas'], vnf['resources'])

        return "ok\n"
    

    def _get_services_deployments_names(self, sfc_name):
        services_list = []
        deployments_list = []
        
        namespace = 'default'

        # config.load_incluster_config() # running inside pod
        config.load_kube_config() # running outside pod        

        v1 = client.CoreV1Api()
        services = v1.list_namespaced_service(watch=False,namespace=namespace)
        
        for service in services.items:
            if sfc_name in str(service.metadata.name):
                services_list.append(service.metadata.name)

        v1 = client.AppsV1Api()
        deployments = v1.list_namespaced_deployment(watch=False,namespace=namespace)

        for deployment in deployments.items:
            if sfc_name in str(deployment.metadata.name):
                deployments_list.append(deployment.metadata.name)
        
        return services_list, deployments_list

    @route("/sfc_request/<id>", methods=["DELETE"])
    def delete_sfc(self, id):
        services_list, deployments_list = self._get_services_deployments_names(id)

        config.load_kube_config() # or config.load_incluster_config()

        api_instance = client.CoreV1Api()

        namespace = 'default'

        # https://stackoverflow.com/questions/64221992/simple-way-to-delete-existing-pods-from-python
        for service_name in services_list:
            try:
                api_response = api_instance.delete_namespaced_service(service_name, namespace)
                # print(api_response)
            except ApiException as e:
                print("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)
        
        api_instance = client.AppsV1Api()

        for deployment_name in deployments_list:
            try:
                api_response = api_instance.delete_namespaced_deployment(deployment_name, namespace)
                # print(api_response)
            except ApiException as e:
                print("Exception when calling CoreV1Api->delete_namespaced_pod: %s\n" % e)

        return 'ok'




if __name__ == '__main__':
    app = Flask(__name__)
    CORS(app)
    EnvironmentController.register(app)
    app.run(host="0.0.0.0", port=4900, debug=True)
    # ec = EnvironmentController()
    # ec._create_docker_image(image_name = 'sfc1_teste', files_path = '/home/guto/Desktop/vnf1/')
    

