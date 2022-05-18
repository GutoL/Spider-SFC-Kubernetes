from flask import Flask
from flask_classful import FlaskView, route, request
from bson import json_util
import json
from flask_cors import CORS
import requests

# some_file.py
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '../repository/')

from infrastructure_repository import InfrastructureRepository
from sfc_request_repository import SfcRequestRepository
from vnf_template_repository import VnfTemplateRepository

class API(FlaskView):
    def __init__(self) -> None:
        f = open('system.config')
        self.config = json.load(f)
        f.close()

        self.vnf_template_repository = VnfTemplateRepository()
        self.sfc_request_repository = SfcRequestRepository()
        self.infrastructure_repository = InfrastructureRepository()
        

    route_base = '/'

    @route('/vnf', methods=['GET'])
    def get_vnfs(self)-> dict:
        vnfs = self.vnf_template_repository.get_all_vnfs()
        return json.dumps(vnfs, indent=4, default=json_util.default)


    @route('/vnf/<vnf_id>', methods=['GET'])
    def get_vnf(self, vnf_id):
        return self.vnf_template_repository.get_vnf_template_by_id(vnf_id)

    @route("/vnf/<vnf_id>", methods=["DELETE"])
    def delete_vnf(self, vnf_id):
        vnfs_templates_deleted = self.vnf_template_repository.delete_vnf_template(vnf_id)

        return json.dumps(vnfs_templates_deleted, indent=4, default=json_util.default)

    
    @route('/infra', methods=['GET'])
    def get_infrastructures(self) -> dict:
        infrastructures = self.infrastructure_repository.get_all_infrastructures()
        return json.dumps(infrastructures, indent=4, default=json_util.default)

    @route('/infra_monitor', methods=['GET'])
    def get_infrastructure_from_monitor(self) -> dict:
        infrastructure = self.infrastructure_repository.get_data_from_monitor(self.config['monitor_ip']+'data')
        return json.dumps(infrastructure, indent=4, default=json_util.default)

    @route('/infra/<infra_name>', methods=['GET'])
    def get_infrastructures_by_name(self, infra_name) -> dict:
        infrastructure = self.infrastructure_repository.get_infrastructure_by_name(infra_name)
        return json.dumps(infrastructure, indent=4, default=json_util.default)

    @route('/sfc_request', methods=['GET'])
    def get_sfcs(self) -> dict:
        sfcs = self.sfc_request_repository.get_all_sfcs()
        return json.dumps(sfcs, indent=4, default=json_util.default)

    
    @route('/sfc_request', methods=['POST'])
    def create_sfc(self) -> str:
        # placement_req = request.json
        placement_req = json.dumps(request.json, indent=4, default=json_util.default)

        try:
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

            # requests.post(self.config['orchestrator_ip']+'sfc_request', placement_req, headers=headers)
            response = requests.post(self.config['monitor_ip']+'sfc_request', placement_req, headers=headers)

            self.insert_sfc_db(response.json())

            return placement_req
        except:
            print('Error in create the SFC placement')
            return 'placement_req' # '''
        
    
    def insert_sfc_db(self, sfc_data):
        print(sfc_data)
        self.sfc_request_repository.insert_sfc_request(sfc_data)

    @route('/insert_sfc_request_db', methods=['POST'])
    def insert_sfc_db_endpoint(self):
        placement_req = json.dumps(request.json, indent=4, default=json_util.default)
        self.insert_sfc_db(placement_req)
        
    @route("/sfc_request/<name>", methods=["DELETE"])
    def delete_sfc_request(self, name):
        
        try:
            sfc_request_deleted = self.sfc_request_repository.delete_sfc_request(name)
            
            # deleting the SFC placed in the kubernetes
            headers = {'content-type': 'application/json'}
            requests.delete(self.config['environment_controller_ip']+'sfc_request/'+str(name),headers=headers)
            
            return json.dumps(sfc_request_deleted, indent=4, default=json_util.default)
        except:
            print('Error in SFC placement deletion...')


if __name__ == '__main__':
    app = Flask(__name__)
    CORS(app)
    API.register(app)
    app.run(host="0.0.0.0", port=3500, debug=True)
