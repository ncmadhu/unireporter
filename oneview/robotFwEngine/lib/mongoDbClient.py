# Author: Madhu Chakravarthy
# Date: 12-04-2017

import os
import json
import logging
from pymongo import MongoClient
from pymongo import IndexModel, ASCENDING 

#Initialize logger
logger = logging.getLogger('appLogger')


class MongoDbClient(object):

    def __init__(self, host, port, dataBase):

        logger.debug("Init Mongo connection")
        self.host = host
        self.port = port
        self.dataBase = dataBase 
        self.client = None

    def connect(self):

        logger.debug("Connecting to Mongo")
        self.client = MongoClient('mongodb://' + self.host + ':' + str(self.port) + '/')


    def close(self):
        logger.debug("Closing connection to Mongo")
        if self.client:
            self.client.close()

    def getCollection(self, collection):

        logger.debug("Getting collection " + collection + " from " + self.dataBase)
        db =  self.client[self.dataBase]
        return db[collection]


    def getDocument(self, collection, filter):

        logger.debug("Getting single document")
        document = collection.find_one(filter)
        return document


    def writeDocument(self, collection, document):

        logger.debug("Writing document to collection")
        result = collection.insert_one(document)
        return result.acknowledged


    def updateDocument(self, collection, filter, newValue):

        logger.debug("Updating document in collection")
        result = collection.update_one(filter, {"$set": newValue})
        return result.acknowledged

    def deleteDocument(self, collection, filter):

        logger.debug("Deleting document in collection")
        result = collection.delete_one(filter)
        return result.acknowledged

    def listIndex(self, collection):

        logger.debug("Listing indexes")
        return collection.list_indexes()

    def createIndexes(self, collection, indexes):

        logger.debug("Creating Indexes")
        collection.create_indexes(indexes)

    def dropIndexes(self, collection):

        logger.debug("Creating Indexes")
        collection.drop_indexes()

    def createIndexModels(self, keyDirections):

        logger.debug("Creating Index Model")
        indexModels = []
        for keyDir in keyDirections:
            indexModels.append(IndexModel([keyDir]))
        return indexModels

    def addData(self, collection, data):

        if data:
            logger.debug("Adding data to mongoDb")
            document = self.getDocument(collection, {"name": data["name"]})
            if document:
                logger.debug("Updating data to mongoDb")
                self.updateDocument(collection, {"name": data["name"]},
                                    {"latest-summary": data["latest-summary"]})
                historicalSummary = [data["latest-summary"]] + \
                                    document.get("historical-summary", [])
                self.updateDocument(collection, {"name": data["name"]},
                                    {"historical-summary": historicalSummary})
            else:
                logger.debug("Adding new data to mongoDb")
                data['historical-summary'] = [data['latest-summary']]
                self.writeDocument(collection, data)


    def addFrameworkData(self, collection, data):

        if data:
            logger.debug("Adding data to mongoDb")
            document = self.getDocument(collection, {"name": data["name"]})
            if document:
                logger.debug("Updating data to mongoDb")
                self.updateDocument(collection, {"name": data["name"]},
                                    {"latest-summary": data["latest-summary"]})
                self.updateDocument(collection, {"name": data["name"]},
                                    {"suite-name": data["suite-name"]})
            else:
                logger.debug("Adding new data to mongoDb")
                self.writeDocument(collection, data)



if __name__ == "__main__":

    import logging.config

    logging.config.fileConfig(os.path.join(os.getcwd(),'..',
                                              'config', 'logging.conf'))
    logger = logging.getLogger('appLogger')
    logger.info("Started testing MongoDbClient")

    def printIndex(indexes):
        for index in indexes:
            print index

    sampleData = {
        "name" : "Demo",
        "latest-summary" : {
            "source" : "/home/madhu/robot/Demo.robot",
            "status" : "PASS",
            "end-time" : "20170414 01:28:01.125",
            "start-time" : "20170414 01:28:01.094",
            "test-summary" : [
                {
                    "status" : "FAIL",
                    "end-time" : "20170414 01:28:01.123",
                    "start-time" : "20170414 01:28:01.121",
                    "name" : "My Test"
                },
                {
                    "status" : "FAIL",
                    "end-time" : "20170414 01:28:01.125",
                    "start-time" : "20170414 01:28:01.123",
                    "name" : "Bad Test"
                }
            ]
        }
    }


    mongoDbClient = MongoDbClient('localhost', 27017, 'test')
    mongoDbClient.connect()
    collection = mongoDbClient.getCollection('suite')
    mongoDbClient.dropIndexes(collection)
    indexes = mongoDbClient.createIndexModels([("name", ASCENDING),
                                     ("latest-summary.status", ASCENDING)])
    mongoDbClient.createIndexes(collection, indexes)
    mongoDbClient.addData(collection, sampleData)
    '''
    mongoDbClient.updateDocument(collection, {"name": "Demo"},{"latest-summary.status": "PASS"})
    mongoDbClient.deleteDocument(collection, {"name": "Demo"})
    printIndex(indexes)
    '''
    mongoDbClient.close()



