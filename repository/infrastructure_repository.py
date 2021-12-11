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
        self.collection_name = 'infrastructure'
    
    def prepare_infra_data(self, infrastructure: dict):
        
        graph = deepcopy(infrastructure['graph'])

        all_nodes = []
        nodes_id = []

        for node in graph.nodes:
            graph.nodes[node]['_id'] = graph.nodes[node]['id']
                
            all_nodes.append(graph.nodes[node])
                
            # nodes_id.append(DBRef("nodes", graph.nodes[node]['_id']))
            nodes_id.append(graph.nodes[node]['_id'])


        all_edges = []
        links_id = []

        for edge in graph.edges:
            graph.edges[edge]['_id'] = str(graph.edges[edge]['src_node'])+'-'+str(graph.edges[edge]['dst_node'])
                
            all_edges.append(graph.edges[edge])

            # links_id.append(DBRef("links", graph.edges[edge]['_id']))
            links_id.append(graph.edges[edge]['_id'])

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
    
    def get_nodes_and_links_from_infra(self, infra_data):
        nodes_list = []
        for node in infra_data['nodes']:
            nodes_list.append(self.node_repository.get_node_by_id(node))
        
        infra_data['nodes'] = nodes_list

        links_list = []
        for link in infra_data['links']:
            links_list.append(self.link_repository.get_link_by_id(link))
        
        infra_data['links'] = links_list

        return infra_data

    def get_all_infrastructures(self) -> list:
        try:

            all_infrastructures = {}

            result = self.db_manager.get_all_collection_data(self.collection_name)            
            
            for infra_data in result:
                all_infrastructures[str(infra_data['_id'])] = self.get_nodes_and_links_from_infra(infra_data)                
                    
            return all_infrastructures

        except BulkWriteError as e:
                # print(e)
                pass
        
    def get_infrastructure_by_name(self, name: str):
        try:
            infra_data = self.db_manager.get_data_by_id_or_name(self.collection_name, name, key='name')
            infra_data = self.get_nodes_and_links_from_infra(infra_data)

            return infra_data

        except BulkWriteError as e:
            # print(e)
            pass


    def update_infrastructure(self, new_data: dict, name: str) -> None:
        try:

            infra_data, all_nodes, all_edges, graph = self.prepare_infra_data(new_data)

            for node in all_nodes:
                self.node_repository.update_node(node, node['_id'])
            for link in all_edges:
                self.link_repository.update_link(link, link['_id'])

            self.db_manager.update_collection_data(self.collection_name, 'name', name, infra_data)
            
        except BulkWriteError as e:
                # print(e)
                pass

    def delete_infrastructure(self, name: str) -> None:
        try:
            infra_data = self.get_infrastructure_by_name(name)
            
            key = '_id'
            for node in infra_data['nodes']:
                self.node_repository.delete_node(str(node[key]))
            
            for node in infra_data['links']:
                self.link_repository.delete_link(str(node[key]))
            
            self.db_manager.delete_collection_data(self.collection_name, name, 'name')

        except BulkWriteError as e:
                # print(e)
                pass