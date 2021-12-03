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
    
    def insert_infra(self, infrastrucure):
        
        try:
            
            graph = deepcopy(infrastrucure['graph'])
            all_nodes = []
            nodes_id = []

            for node in graph.nodes:
                graph.nodes[node]['_id'] = graph.nodes[node]['id']
                
                all_nodes.append(graph.nodes[node])
                
                nodes_id.append(DBRef("nodes", graph.nodes[node]['_id']))

            self.node_repository.insert_nodes(all_nodes)

            all_edges = []
            links_id = []

            for edge in graph.edges:
                graph.edges[edge]['_id'] = str(graph.edges[edge]['src_node'])+'-'+str(graph.edges[edge]['dst_node'])
                
                all_edges.append(graph.edges[edge])

                links_id.append(DBRef("links", graph.edges[edge]['_id']))
            
            self.link_repository.inser_links(all_edges)

            infra_data = {'name': infrastrucure['name'],
                         'nodes': nodes_id,
                         'links': links_id}

            self.db_manager.create_connection()
            self.db_manager.insert_data_into_collection('infrastructure', [infra_data])
            self.db_manager.close_connection()

        except BulkWriteError as e:
                # print(e)
                pass
