from data_base_manager import DataBaseManager
from pymongo.errors import BulkWriteError

class LinkRepository():
    def __init__(self) -> None:
        self.db_manager = DataBaseManager()
    
    def inser_link(self, data):
        self.db_manager.create_connection()

        try:
            self.db_manager.insert_data_into_collection('links', data)
        except BulkWriteError as e:
                # print(e)
                pass
        self.db_manager.close_connection()
