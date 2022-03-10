import random
from flask_classful import FlaskView, route, request
from flask import Flask
import networkx as nx
import requests
from infra_graph import InfrastructureGraph
from graph_handler import InfrastructureGraphHandler
import copy
import numpy as np
import json
from flask_cors import CORS


class Agent(FlaskView):
    def __init__(self) -> None:
        super().__init__()
        f = open('system.config')
        self.config = json.load(f)
        f.close()

    route_base = '/'

    def _get_node_name_from_id(self, id, graph):
        for node in graph.nodes:
            if id == graph.nodes[node]['id']:
                return graph.nodes[node]['name']
        return id

    def _get_node_id_from_name(self, name, graph):
        for node in graph.nodes:
            if name == graph.nodes[node]['name']:
                return graph.nodes[node]['id']
        return name

    # @route('/placement', methods=['POST'])
    # def place_vnf(self)-> dict:
    #    placement_req = request.json
    def place_vnf(self, placement_req)-> dict:    
        infrastructure_graph = InfrastructureGraph(placement_req['graph']['nodes'], placement_req['graph']['edges'])

        # print('################')
        # for n in infrastructure_graph.nodes:
        #     print(n,infrastructure_graph.nodes[n])
        # print('----------')

        # for e in infrastructure_graph.edges:
        #     print(e, infrastructure_graph.edges[e])
        # print('-------------')

        igh = InfrastructureGraphHandler(infrastructure_graph)

        k = 3

        placement_decision = {
            "name":   placement_req['sfc_info']['name'],
            "source": placement_req['sfc_info']['source'],
            "destination": placement_req['sfc_info']['destination'],
            "VNFs": [],
            "flow_entries": []
        }

        temp_source_node = placement_req['sfc_info']['source']

        weight = 'delay'

        for i, vnf in enumerate(placement_req['vnfs']):
            candidate_nodes = igh.get_candidate_nodes(vnf['id'],
                                                    placement_req['sfc_info']['source'],
                                                    placement_req['sfc_info']['destination'],
                                                    vnf['resources'],
                                                    placement_req['flow_entries'][i]['resources'], k)
            
            print('candidate_nodes',candidate_nodes)
            nodes_consumption = igh.graph.get_nodes_consumption(aggregated=False, nodes=candidate_nodes)

            nodes_names = list(nodes_consumption.keys())

            for node in nodes_consumption:
                if type(node) == int and node < 0:
                    continue
                nodes_consumption[node]['availability'] = copy.copy(igh.graph.nodes[node]['availability'])

            nodes_consumption = [v2 for k1,v1 in nodes_consumption.items() for k2,v2 in v1.items()]

            obs = nodes_consumption
            obs += list(vnf['resources'].values())
            obs += [placement_req['sfc_info']['requirements']['availability']]
            obs = np.array(obs)

            # call the trained agent to select the candidate node and define the redundancy
            candidate_node, redundancy = self._define_placement(obs)

            candidate_node = nodes_names[candidate_node]

            placement_decision['VNFs'].append(
                {"name":vnf['name'],
                 "node_id": candidate_node,
                 "node_name":igh.graph.nodes[str(candidate_node)]['name'],
                 "replicas":redundancy+1,
                 "resources":vnf['resources']
                }
            )

            # print('temp_source_node',temp_source_node)
            temp_source_node = self._get_node_id_from_name(temp_source_node, igh.graph)

            shortest_path = nx.shortest_path(igh.graph,source=str(temp_source_node), target=str(candidate_node), weight=weight)

            shortest_path_links = [(shortest_path[j], shortest_path[j+1]) for j in range(len(shortest_path)-1)]
            
            placement_decision['flow_entries'].append(
                {   
                    "vnf_name": vnf['name'],
                    "source": temp_source_node,
                    "destination": candidate_node,
                    "path": shortest_path_links
                }
            )

            temp_source_node = candidate_node


        # temp_source_node = self._get_node_id_from_name(temp_source_node, igh.graph)
        destination_node = self._get_node_id_from_name(placement_req['sfc_info']['destination'], igh.graph)

        shortest_path = nx.shortest_path(igh.graph,source=str(temp_source_node), target=str(destination_node), weight=weight)

        shortest_path_links = [(shortest_path[x], shortest_path[x+1]) for x in range(len(shortest_path)-1)]

        placement_decision['flow_entries'].append(
            {   
                "vnf_name": 'destination',
                "source": temp_source_node,
                "destination": destination_node,
                "path": shortest_path_links
            }
        )

        placement_decision['graph'] = placement_req['graph']
        
        return placement_decision
    
    def _define_placement(self, obs):
        # number_of_candidate_nodes = int((len(obs)-4)/4)-1
        # candidate = random.randint(0,number_of_candidate_nodes)
        candidate = 0

        redundancy = random.randint(0,1)

        return candidate, redundancy

    @route('/sfc_request', methods=['POST'])
    def create_sfc(self)-> str:
        placement_decision = self.place_vnf(request.json)

        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        response = requests.post(self.config['environment_controller_ip']+'sfc_request',json=placement_decision, headers=headers)
        return response.text


if __name__ == '__main__':
    app = Flask(__name__)
    CORS(app)
    Agent.register(app)
    app.run(host="0.0.0.0", port=4998, debug=True)


