from data_base_manager import DataBaseManager
from node_respository import NodeRepository
from link_repository import LinkRepository
from copy import deepcopy
from bson.dbref import DBRef
from pymongo.errors import BulkWriteError


class InfrastructureRepository():
    def __init__(self) -> None:
        self.db_manager = DataBaseManager()
        self.node_repository = NodeRepository()
        self.link_repository = LinkRepository()
        self.collection_name = 'infrastructures'
    
    def prepare_infra_data(self, infrastructure: dict):
        
        graph = deepcopy(infrastructure['graph'])

        all_nodes = []
        nodes_id = []

        for node in graph.nodes:
            graph.nodes[node]['_id'] = graph.nodes[node]['id']
                
            all_nodes.append(graph.nodes[node])
                
            nodes_id.append(DBRef("nodes", graph.nodes[node]['_id']))

        all_edges = []
        links_id = []

        for edge in graph.edges:
            graph.edges[edge]['_id'] = str(graph.edges[edge]['src_node'])+'-'+str(graph.edges[edge]['dst_node'])
                
            all_edges.append(graph.edges[edge])

            links_id.append(DBRef("links", graph.edges[edge]['_id']))

        infra_data = {'name': infrastructure['name'],
                    'nodes': nodes_id,
                    'links': links_id}
        
        return infra_data, all_nodes, all_edges, graph
        
    def insert_infrastructure(self, infrastructure: dict) -> None:
        
        try:
            
            infra_data, all_nodes, all_edges, graph = self.prepare_infra_data(infrastructure)

            self.node_repository.insert_nodes(all_nodes)
            self.link_repository.insert_links(all_edges)           

            self.db_manager.insert_data_into_collection(self.collection_name, [infra_data])
            

        except BulkWriteError as e:
                # print(e)
                pass
    
    def get_all_infrastructures(self) -> list:
        try:
            all_infrastructures = self.db_manager.get_all_collection_data(self.collection_name)
            return all_infrastructures

        except BulkWriteError as e:
                # print(e)
                pass

    def update_infrastructure(self, new_data: dict, name: str) -> None:
        try:

            infra_data, all_nodes, all_edges, graph = self.prepare_infra_data(new_data)

            for node in all_nodes:
                self.node_repository.update_node(node, node['name'])
            for link in all_edges:
                self.link_repository.update_link(link, link['_id'])

            self.db_manager.update_collection_data(self.collection_name, 'name', name, infra_data)
            
        except BulkWriteError as e:
                # print(e)
                pass

    def delete_infrastructure(self, name: str) -> None:
        try:
            self.db_manager.delete_collection_data(self.collection_name, name)

        except BulkWriteError as e:
                # print(e)
                pass