from infra import InfrastructureGraph
import pymongo
import networkx as nx


class GraphHandler():
  def __init__(self, url):
    self.url = url
  
  def _create_connection(self, database_name):
    myclient = pymongo.MongoClient(self.url)
    mydb = myclient[database_name]

    return mydb

  def graph_to_db(self, graph, database_name):
    
    mydb = self._create_connection(database_name)

    all_nodes = []
    for node in infrastructure_graph.nodes:
      all_nodes.append(infrastructure_graph.nodes[node])

    all_edges = []
    for edge in infrastructure_graph.edges:
      all_edges.append(infrastructure_graph.edges[edge])

    mycol = mydb["nodes"]
    x = mycol.insert_many(all_nodes)

    mycol = mydb["edges"]
    x = mycol.insert_many(all_edges)
    

  def db_to_graph(self, database_name):
    mydb = self._create_connection(database_name)

    G = nx.Graph()
    
    mycol = mydb["nodes"]
    all_nodes = [(int(node['id']), node) for node in list(mycol.find())]
    G.add_nodes_from(all_nodes)

    mycol = mydb['edges']
    all_edges = [(int(edge['src_node']), int(edge['dst_node']), edge) for edge in list(mycol.find())]
    G.add_edges_from(all_edges)
    
    return G

  def update_node(self, database_name, node_id, new_data):
    mydb = self._create_connection(database_name)

    mycol = mydb["nodes"]

    myquery = {"id": str(node_id)}
    newvalues = {"$set": new_data}

    mycol.update_one(myquery, newvalues)
  
  def update_ege(self, database_name, source_node_id, destination_node_id, new_data):
    mydb = self._create_connection(database_name)

    mycol = mydb["edges"]

    myquery = {"src_node": source_node_id,"dst_node":destination_node_id}
    newvalues = {"$set": new_data}

    mycol.update_one(myquery, newvalues)

  def delete_graph_from_db(self, db_name):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient.drop_database(db_name)


# --------------------------------------------------------------------------------
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

graph_as = None
infrastructure_graph = InfrastructureGraph(graph_as=graph_as,AS_number=50,latitude=19.99,longitude=73.78,
                                  lat_list=None, long_list=None,
                                  resources_ranges=resources_ranges,
                                  vnf_list=vnf_list,nodes_support_all_vnfs=False,
                                  add_fat_tree=False,
                                  servers_number_micro=2, servers_number=4,
                                  add_clusters=True)

graph_handler = GraphHandler("mongodb://localhost:27017/")
db_name = "infrastructure"

## Saving graph
# graph_handler.graph_to_db(infrastructure_graph, db_name)

## Loading graph
# graph = graph_handler.db_to_graph(db_name)
# print(graph.number_of_nodes())
# print(graph.number_of_edges())

## Updating node
# node_id = 49
# new_data = {'type': 'CC', 'peers': 0, 'latitude': 19.998697576592633, 'longitude': 73.78690315061714, 'status': 'operational', 'resources': {'cpu': 10, 'memory': 10, 'storage': 10}, 'node_cost': 500, 'mttf': 2880, 'mttr': 1.5, 'availability': 0.9994794377928162, 'energy': 20, 'metadata': [[{'metadata_key': 'lat', 'value': 19.998697576592633}, {'metadata_key': 'long', 'value': 73.78690315061714}]], 'capabilities': {'supported_VNFs': [{'id': 2, 'type': 'DPI'}, {'id': 0, 'type': 'load balance'}]}, 'available_resources': {'cpu': 10, 'memory': 10, 'storage': 10}, 'id': '49', 'original_id': '49', 'name': 'node_name_49', 'ports': ['s49p0'], 'placed': {}, 'cluster': 4}
# graph_handler.update_node(db_name, node_id, new_data)

## Updating edge
# source_node = 12
# destination_node = 13
# new_data = {'type': 'peer', 'customer': 'Gutoooo', 'id': 78, 'src_port': 's12p5', 'dst_port': 's13p2', 'src_node': 12, 'dst_node': 13, 'resources': {'delay': 0.5564765526145907, 'bandwidth': 10, 'cost_link': 10}, 'available_resources': {'delay': 0.5564765526145907, 'bandwidth': 10, 'cost_link': 10}}
# graph_handler.update_ege(db_name, source_node, destination_node, new_data)

## Deleting graph
# graph_handler.delete_graph_from_db(db_name)


