import requests
import networkx as nx
from networkx.readwrite import json_graph
import copy

from graph_handler import GraphHandler

from flask import Flask

def graph_from_monitor(ip):
    r = requests.get(ip)
    data = r.json()
    
    G = nx.Graph()

    all_components = []
    
    for node in data['nodes']:
        # node_id = node.pop('id')
        node_id = node['id']
        all_components.append((node_id,node))
    
    G.add_nodes_from(all_components)
    
    gw_nodes = {}
    all_components = []

    for link in data['edges']:
        
        if link['destination']['id'] not in gw_nodes:
            gw_nodes[link['destination']['id']] = link['destination']

        source = link.pop('source')
        destination = link.pop('destination')

        link['src_node'] = source['id']
        link['dst_node'] = destination['id']

        link['src_port'] = source['port']
        link['dst_port'] = destination['port']
        
        all_components.append((link['src_node'], link['dst_node'], link))
    
    G.add_edges_from(all_components)

    nx.set_node_attributes(G, gw_nodes) # adding attributes to gateway nodes

    return G

app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    # Define if this code will be either a thread or an API
    ip = "http://192.168.0.209:4997/data" # MONITOR IP
    infrastructure_graph = graph_from_monitor(ip)

    # for edge in infrastructure_graph.edges:
    #     print(infrastructure_graph.edges[edge])
        # break

    graph_handler = GraphHandler("mongodb://localhost:27017/")
    db_name = "infrastructure"

    # Saving graph
    graph_handler.graph_to_db(copy.deepcopy(infrastructure_graph), db_name)

    # print('Number of nodes:',infrastructure_graph.number_of_nodes())
    # print('Number of edges:',graph.number_of_edges())

    # for node in infrastructure_graph.nodes:
    #     print(node,infrastructure_graph.nodes[node])
    #     print('--------------')

    # for edge in infrastructure_graph.edges:
    #     print(edge, infrastructure_graph.edges[edge])
    #     print('--------------')

    data = json_graph.node_link_data(infrastructure_graph)
    
    return data

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4999, debug=True)


