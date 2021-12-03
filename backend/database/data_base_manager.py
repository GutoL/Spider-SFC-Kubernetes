import pymongo
from pymongo.errors import BulkWriteError

class DataBaseManager():
    
    def __init__(self, url="mongodb://localhost:27017/", db_name="SPIDER"):
        self.url = url
        self.db_name = db_name
  
    def create_connection(self):
        self.myclient = pymongo.MongoClient(self.url)
        mydb = self.myclient[self.db_name]

        return mydb

    def close_connection(self):
        self.myclient.close()

    def insert_data_into_collection(self, collection_name, data):
        
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
    
    def get_all_collection_data(self, collection_name):
        my_db = self.create_connection()

        try:
            my_collection = my_db[collection_name]
            cursor = my_collection.find({})
            
            data = []
            for document in cursor:
                data.append(document)
            
            return data
        except BulkWriteError as e:
            pass
            
        self.close_connection()
    
    def update_collection_data(self, collection_name, id, new_data):
        my_db = self.create_connection()

        try:
            my_collection = my_db[collection_name]

            myquery = {"id": str(id)}
            newvalues = {"$set": new_data}

            my_collection.update_one(myquery, newvalues)
        except BulkWriteError as e:
            pass

        self.close_connection()

    def delete_collection_data(self, collection_name, id):

        my_db = self.create_connection()

        try:
            my_collection = my_db[collection_name]

            myquery = {"id": str(id)}
            my_collection.delete_one(myquery)

        except BulkWriteError as e:
            pass

        self.close_connection()

