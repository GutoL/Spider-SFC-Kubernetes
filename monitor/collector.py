import requests
import networkx as nx

def graph_from_monitor(ip = 'http://192.168.255.106:5000/'):
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
    
graph = graph_from_monitor()

print(graph.number_of_nodes())
print(graph.number_of_edges())

for node in graph.nodes:
    print(node,graph.nodes[node])
    print('--------------')

for edge in graph.edges:
    print(edge, graph.edges[edge])
    print('--------------')