import requests
import networkx as nx
from graph_handler import GraphHandler

def graph_from_monitor(ip):
    r = requests.get(ip)
    data = r.json()
    
    G = nx.Graph()

    all_components = []
    for node in data['nodes']:
        node_id = node.pop('id')
        all_components.append((node_id,node))
    
    G.add_nodes_from(all_components)
    
    all_components = []
    for link in data['links']:
        
        source = link.pop('source')
        destination = link.pop('destination')

        link['src_node'] = source['id']
        link['dst_node'] = destination['id']

        link['src_port'] = source['port']
        link['dst_port'] = destination['port']
        
        all_components.append((link['src_node'], link['dst_node'], link))
    
    G.add_edges_from(all_components)

    return G

if __name__ == '__main__':
    # Define if this code will be either a thread or an API
    ip = "http://192.168.0.184:5000/"    
    infrastructure_graph = graph_from_monitor(ip)

    graph_handler = GraphHandler("mongodb://localhost:27017/")
    db_name = "infrastructure"

    # Saving graph
    graph_handler.graph_to_db(infrastructure_graph, db_name)

    # print('Number of nodes:',infrastructure_graph.number_of_nodes())
    # print('Number of edges:',graph.number_of_edges())

    # for node in infrastructure_graph.nodes:
    #     print(node,infrastructure_graph.nodes[node])
    #     print('--------------')

    # for edge in infrastructure_graph.edges:
    #     print(edge, infrastructure_graph.edges[edge])
    #     print('--------------')