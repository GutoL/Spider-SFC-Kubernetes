import random
from flask_classful import FlaskView, route, request
from flask import Flask
import networkx as nx
from infra_graph import InfrastructureGraph
from graph_handler import InfrastructureGraphHandler
import copy
import numpy as np

class Agent(FlaskView):
    def __init__(self) -> None:
        super().__init__()

    route_base = '/'

    @route('/placement', methods=['POST'])
    def place_vnf(self)-> dict:
        placement_req = request.json
        
        infrastructure_graph = InfrastructureGraph(placement_req['graph']['nodes'], placement_req['graph']['edges'])

        # print('################')
        # for n in infrastructure_graph.nodes:
        #     print(n,infrastructure_graph.nodes[n])
        # print('----------')
        # for e in infrastructure_graph.edges:
        #     print(e, infrastructure_graph.edges[e])
        
        igh = InfrastructureGraphHandler(infrastructure_graph)

        k = 2

        placement_decision = {
            "name":   placement_req['sfc_info']['name'],
            "source": placement_req['sfc_info']['source'],
            "destination": placement_req['sfc_info']['destination'],
            "VNFs": []
        }

        for i, vnf in enumerate(placement_req['vnfs']):
            candidate_nodes = igh.get_candidate_nodes(vnf['id'],
                                                    placement_req['sfc_info']['source'],
                                                    placement_req['sfc_info']['destination'],
                                                    vnf['resources'],
                                                    placement_req['flow_entries'][i]['resources'], k)
            
            nodes_consumption = igh.graph.get_nodes_consumption(aggregated=False, nodes=candidate_nodes)

            for node in nodes_consumption:
                nodes_consumption[node]['availability'] = copy.copy(igh.graph.nodes[node]['availability'])

            nodes_consumption = [v2 for k1,v1 in nodes_consumption.items() for k2,v2 in v1.items()]

            obs = nodes_consumption
            obs += list(vnf['resources'].values())
            obs += [placement_req['sfc_info']['requirements']['availability']]
            obs = np.array(obs)

            # call the trained agent to select the candidate node and define the redundancy
            candidate_node, redundancy = self._define_placement(obs)

            placement_decision['VNFs'].append(
                {"name":vnf['name'],
                 "node":igh.graph.nodes[str(candidate_node)]['name'],
                 "replicas":redundancy+1,
                 "resources":vnf['resources']
                }
            )

        return placement_decision
    
    def _define_placement(self, obs):
        number_of_candidate_nodes = int((len(obs)-4)/4)-1
        candidate = random.randint(0,number_of_candidate_nodes)

        redundancy = random.randint(0,1)

        return candidate, redundancy
        

    
        
app = Flask(__name__)
Agent.register(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4998, debug=True)


