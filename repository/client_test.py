# import requests
# import networkx as nx
# from networkx.readwrite import json_graph
# import copy
import pandas as pd
from infra import InfrastructureGraph
from infrastructure_repository import InfrastructureRepository
from sfc_request_repository import SfcRequestRepository
from vnf_template_repository import VnfTemplateRepository

basic_path = "/home/guto/vnf_catalog/"

vnfs = [
    {
      "name": "firewall",
      "_id": "0",
      "id": "0",
      "resources": {"cpu": 1,"memory": 1,"storage": 1},
      "mttf": 1,
      "mttr": 1,
      "availability": 1,
      "path_to_files": basic_path+"firewall"
    },
    {
      "name": "compress-image",
      "_id": "1",
      "id": "1",
      "resources": {"cpu": 1,"memory": 1,"storage": 1},
      "mttf": 1,
      "mttr": 1,
      "availability": 1,
      "path_to_files": basic_path+"compress-image"
    },
    {
      "name": "face-detection",
      "_id": "2",
      "id": "2",
      "resources": {"cpu": 1,"memory": 1,"storage": 1},
      "mttf": 1,
      "mttr": 1,
      "availability": 1,
      "path_to_files": basic_path+"face-detection"
    }
  ]

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

city_data = pd.read_csv('worldcities.csv')
city_data = city_data[['lat','lng']].tail(number_of_nodes)

lat_list = city_data['lat'].values
long_list = city_data['lng'].values

infrastructure_graph = InfrastructureGraph(graph_as=None,AS_number=number_of_nodes,
                                            latitude=None,longitude=None,
                                            lat_list=lat_list, long_list=long_list,
                                            resources_ranges=resources_ranges,
                                            vnf_list=vnf_list,nodes_support_all_vnfs=False,
                                            add_fat_tree=False,
                                            servers_number_micro=2, servers_number=4,
                                            add_clusters=True)

infra_repository = InfrastructureRepository()
infra_data = {"name": "my_infra", "graph": infrastructure_graph}


sfc_request_repository = SfcRequestRepository()

vnf_template_repository = VnfTemplateRepository()

# # create
# infra_repository.insert_infrastructure(infra_data)
# sfc_request_repository.insert_sfc_request(sfc_request)
vnf_template_repository.insert_vnf_templates(vnfs)

# # get
# infras = infra_repository.get_all_infrastructures()
# for x in infras:
#     print(infras[x]['nodes'])
#     print('----------------------')
#     print(infras[x]['links'])
# print(infra_repository.get_data_from_monitor("http://192.168.0.209:4997/data"))
  
# # update
# infra_data['name'] = 'teste'
# infra_repository.update_infrastructure(infra_data, "my_infra")

# # delete
# infra_repository.delete_infrastructure('my_infra')

print('done!')
