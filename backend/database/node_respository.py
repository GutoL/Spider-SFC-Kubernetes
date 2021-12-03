from data_base_manager import DataBaseManager
from pymongo.errors import BulkWriteError

class NodeRepository():
    def __init__(self) -> None:
        self.db_manager = DataBaseManager()
        self.collection_name = 'nodes'

    def insert_nodes(self, data: dict)->None:
        try:
            self.db_manager.insert_data_into_collection(self.collection_name, data)
            
        except BulkWriteError as e:
                # print(e)
                pass

    def update_node(self, new_data: dict, name: str) -> None:
        self.db_manager.update_collection_data(self.collection_name, 'name', name, new_data)
        