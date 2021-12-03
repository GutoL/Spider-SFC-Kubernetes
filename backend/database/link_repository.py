from data_base_manager import DataBaseManager
from pymongo.errors import BulkWriteError

class LinkRepository():
    def __init__(self) -> None:
        self.db_manager = DataBaseManager()
        self.collection_name = 'links'
    
    def insert_links(self, data: dict) -> None:
        
        try:
            self.db_manager.insert_data_into_collection(self.collection_name, data)
        except BulkWriteError as e:
                # print(e)
                pass
        
    def update_link(self, new_data: dict, id: str) -> None:
        self.db_manager.update_collection_data(self.collection_name, '_id', id, new_data)
        
