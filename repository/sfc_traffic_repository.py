from data_base_manager import DataBaseManager
# https://levelup.gitconnected.com/time-series-data-in-mongodb-and-python-fccfb6c1a923

class SfcTrafficRepository():
    def __init__(self) -> None:
        self.db_manager = DataBaseManager()
        self.collection_name = 'sfc_traffic'

    def insert_measurement(self, sfc_id, traffic, physical_links):

        my_db = self.db_manager.create_connection()
        my_collection = my_db[self.collection_name]

        my_collection.update_one(
            # {'sfc-id': sfc_id, 'd': time},
            {'sfc-id': sfc_id, 'physical_links': physical_links},
            {
                # '$push': {'samples': data, 'd': time},
                '$push': {'traffic': traffic},
                '$inc': {'nsamples': 1}
            }, upsert=True
        )
    
    def get_sfc_traffic_by_id(self, id: str, key:str='sfc-id'):
        return self.db_manager.get_data_by_id_or_name(self.collection_name, id)
    
    def get_sfc_traffic_by_sfc_id(self, id: str):
        return self.db_manager.get_data_by_id_or_name(collection_name=self.collection_name, 
                    id=id, key='sfc-id', find_one=False)

    # def update_node(self, new_data: dict, id: str) -> None:
    #     self.db_manager.update_collection_data(self.collection_name, '_id', id, new_data)

    def delete_sfc_traffic(self, id: str, key:str='sfc-id'):
        self.db_manager.delete_collection_data(self.collection_name, id, key)