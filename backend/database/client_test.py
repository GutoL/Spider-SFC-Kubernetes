# import requests
# import networkx as nx
# from networkx.readwrite import json_graph
# import copy
from infra import InfrastructureGraph
from infrastructure_repository import InfrastructureRepository

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

infra_repository.insert_infra(infra_data)


print('done!')