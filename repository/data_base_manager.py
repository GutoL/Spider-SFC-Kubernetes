import pymongo
from pymongo.errors import BulkWriteError

class DataBaseManager():
    
    def __init__(self, url: str = "mongodb://localhost:27017/", db_name: str = "SPIDER"):
        self.url = url
        self.db_name = db_name
  
    def create_connection(self):
        self.myclient = pymongo.MongoClient(self.url)
        mydb = self.myclient[self.db_name]

        return mydb

    def close_connection(self):
        self.myclient.close()

    def insert_data_into_collection(self, collection_name: str, data: dict):
        
        my_db = self.create_connection()
        my_collection = my_db[collection_name]

        if len(data) == 1:
            try:
                my_collection.insert_one(data[0])
            except BulkWriteError as e:
                # print(e)
                pass
        else:
            try:
                my_collection.insert_many(data)
            except BulkWriteError as e:
                # print(e)
                pass
        
        self.close_connection()
    
    def get_all_collection_data(self, collection_name: str):
        
        try:
            my_db = self.create_connection()

            my_collection = my_db[collection_name]
            cursor = my_collection.find({})
            
            data = []
            for document in cursor:
                data.append(document)

            self.close_connection()
                
            return data
        except BulkWriteError as e:
            pass
           
    def get_data_by_id_or_name(self, collection_name: str, id: str, key='_id') -> dict:
        try:
            my_db = self.create_connection()

            my_collection = my_db[collection_name]

            data = my_collection.find_one({key: id})

            self.close_connection()

            return data
            
        except BulkWriteError as e:
            pass

    
    def update_collection_data(self, collection_name: str, key: str, key_value: str, new_data: dict):
        
        try:
            my_db = self.create_connection()

            my_collection = my_db[collection_name]

            myquery = {key: key_value}
            newvalues = {"$set": new_data}

            my_collection.update_one(myquery, newvalues)

            self.close_connection()

        except BulkWriteError as e:
            pass

        

    def delete_collection_data(self, collection_name: str, value: str, key: str):

        try:
            my_db = self.create_connection()
            my_collection = my_db[collection_name]

            myquery = {key: value}
            my_collection.delete_one(myquery)

            self.close_connection()

        except BulkWriteError as e:
            pass

        

