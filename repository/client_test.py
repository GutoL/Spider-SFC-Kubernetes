# import requests
# import networkx as nx
# from networkx.readwrite import json_graph
# import copy
from infra import InfrastructureGraph
from infrastructure_repository import InfrastructureRepository
from sfc_request_repository import SfcRequestRepository

# master-node = 0, minion-1 = 1, router-1 = 2
sfc_request = {
    "VNFs": [
        {
            "name": "compress-image",
            "node_name": "0",
            "replicas": 1,
            "resources": {
                "cpu": 1,
                "memory": 0.2,
                "storage": 0.11
            }
        },
        {
            "name": "firewall",
            "node_name": "1",
            "replicas": 1,
            "resources": {
                "cpu": 1,
                "memory": 0.2,
                "storage": 0.11
            }
        }
    ],
    "destination": "1",
    "flow_entries": [
        {
            "destination": "0",
            "path": [],
            "source": "0"
        },
        {
            "destination": "1",
            "path": [
                [
                    "0",
                    "2"
                ],
                [
                    "2",
                    "1"
                ]
            ],
            "source": "0"
        }
    ],
    "name": "my-sfc",
    "source": "0"
}
# ---------------------------------------------------------------------------------------------------

resources_ranges = {
    'cpu': 10,
    'memory': 10,
    'storage': 10,
    'node_cost':500,
    'bandwidth': 10,
    'cost_edge': 10,
    'mttf_node':2880,
    'mttr_node':1.5,
    'energy':20,
    'variability': 0.0001
}

vnf_list = [
            {'id': 0, 'type': 'load balance'},
            {'id': 1, 'type': 'IDS'},
            {'id': 2, 'type': 'DPI'},
            {'id': 3, 'type': 'data compression'}
          ]

number_of_nodes = 10
infrastructure_graph = InfrastructureGraph(graph_as=None,AS_number=number_of_nodes,
                                            latitude=19.99,longitude=73.78,
                                            lat_list=None, long_list=None,
                                            resources_ranges=resources_ranges,
                                            vnf_list=vnf_list,nodes_support_all_vnfs=False,
                                            add_fat_tree=False,
                                            servers_number_micro=2, servers_number=4,
                                            add_clusters=True)

infra_repository = InfrastructureRepository()
infra_data = {"name": "my_infra", "graph": infrastructure_graph}


sfc_request_repository = SfcRequestRepository()

# # create
infra_repository.insert_infrastructure(infra_data)
sfc_request_repository.insert_sfc_request(sfc_request)

# # get
# infras = infra_repository.get_all_infrastructures()
# for x in infras:
#     print(infras[x]['nodes'])
#     print('----------------------')
#     print(infras[x]['links'])
  
# # update
# infra_data['name'] = 'teste'
# infra_repository.update_infrastructure(infra_data, "my_infra")

# # delete
# infra_repository.delete_infrastructure('my_infra')

print('done!')