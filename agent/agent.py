from flask_classful import FlaskView, route, request
from flask import Flask
import networkx as nx

class Agent(FlaskView):
    route_base = '/'

    @route('/placement', methods=['POST'])
    def place_vnf(self)-> str:
        placement_req = request.json
        print('se liga',placement_req)

        graph_json = placement_req['graph']
        vnf = placement_req['vnf']

        print(graph_json)
        print(vnf)
        
        G = nx.Graph()
        
        all_nodes = [(node['id'],node) for node in graph_json['nodes']]
        G.add_nodes_from(all_nodes)

        all_edges = [(edge['src_node'], edge['dst_node'], edge) for edge in  graph_json['links']]
        G.add_edges_from(all_edges)

        return ''


app = Flask(__name__)
Agent.register(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4998, debug=True)


