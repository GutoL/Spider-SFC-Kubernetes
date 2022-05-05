from data_base_manager import DataBaseManager
from pymongo.errors import BulkWriteError
# from bson.dbref import DBRef

class SfcRequestRepository():
    def __init__(self) -> None:
        self.db_manager = DataBaseManager()
        self.collection_name = 'sfc_request'
    
    def insert_sfc_request(self, sfc_request: dict)-> None:
        
        try:
            for i in range(len(sfc_request['VNFs'])):
                # sfc_request['VNFs'][i]['node_name'] = DBRef("nodes", sfc_request['VNFs'][i]['node_name'])
                sfc_request['VNFs'][i]['node_name'] = sfc_request['VNFs'][i]['node_name']

            for i in range(len(sfc_request['flow_entries'])):
                # sfc_request['flow_entries'][i]['destination'] = DBRef("nodes", sfc_request['flow_entries'][i]['destination'])
                sfc_request['flow_entries'][i]['destination'] = sfc_request['flow_entries'][i]['destination']
                
                # sfc_request['flow_entries'][i]['source'] = DBRef("nodes", sfc_request['flow_entries'][i]['source'])
                sfc_request['flow_entries'][i]['source'] = sfc_request['flow_entries'][i]['source']

                new_path_list = []
                for j in range(len(sfc_request['flow_entries'][i]['path'])):
                    # new_path_list.append(DBRef("links", sfc_request['flow_entries'][i]['path'][j][0]+'-'+sfc_request['flow_entries'][i]['path'][j][1]))
                    new_path_list.append(sfc_request['flow_entries'][i]['path'][j][0]+'-'+sfc_request['flow_entries'][i]['path'][j][1])
                
                sfc_request['flow_entries'][i]['path'] = new_path_list
            
            self.db_manager.insert_data_into_collection(self.collection_name,[sfc_request])

        except BulkWriteError as e:
                # print(e)
                pass
    
    def get_all_sfcs(self):
        return self.db_manager.get_all_collection_data(self.collection_name)
    
    def get_sfc_by_name(self, name: str):
        self.db_manager.get_data_by_id_or_name(self.collection_name, name, 'name')

    def delete_sfc_request(self, name: str):
        self.db_manager.delete_collection_data(self.collection_name, name, 'name')
