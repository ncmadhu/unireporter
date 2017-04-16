# Author: Madhu Chakravarthy
# Date: 12-04-2017

import os
import rabbitMQ
import mongoDbClient
import ConfigParser
import logging
import logging.config
from pymongo import IndexModel, ASCENDING

#Initialize logger

logging.config.fileConfig(os.path.join(os.getcwd(),'..', 'config', 'logging.conf'))
logger = logging.getLogger('appLogger')

class AppMain(object):
    
    def __init__(self):

        logger.info("Info Starting App")
        self.rabbitMQ = None
        self.config = self.loadConfig()
        self.framework = self.config.get('Framework', 'name')
        self.initRabbitMQConfig()
        self.initMongoDbConfig()

    def loadConfig(self):

        logger.debug("Loading configuration")
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.getcwd(), '..', 'config', 'config.ini'))
        logger.debug("Config Sections: " + str(config.sections()))
        return config

    def initRabbitMQConfig(self):

        logger.debug("Initializing rabbitMQ config")
        self.rabbitMQHost = self.config.get('RabbitMQ', 'host')
        self.rabbitMQPort = int(self.config.get('RabbitMQ', 'port'))
        self.rabbitMQUserName = self.config.get('RabbitMQ', 'username')
        self.rabbitMQPassword = self.config.get('RabbitMQ', 'password')
        self.rabbitMQExchange = self.config.get('RabbitMQ', 'exchange')
        self.rabbitMQReceiveQueue = self.config.get('RabbitMQ', 'receiveQueue')
        receiveRoutingKeys = self.config.get('RabbitMQ', 'receiveRoutingKeys')
        self.rabbitMQReceiveRoutingKeys = receiveRoutingKeys.split(',')

    def initMongoDbConfig(self):

        logger.debug("Initializing MongoDb config")
        self.mongoHost = self.config.get('MongoDB', 'host')
        self.mongoPort = self.config.get('MongoDB', 'port')
        self.mongoDb = self.config.get('MongoDB', 'database')

    def connectToRabbitMQ(self):

        logger.debug("Connecting to rabbitMQ")
        self.rabbitMQ = rabbitMQ.RabbitMQ(self.rabbitMQHost,
                                 self.rabbitMQPort,
                                 self.rabbitMQUserName,
                                 self.rabbitMQPassword)
        return self.rabbitMQ

    def createMongoIndexes(self):

        mongoClient = mongoDbClient.MongoDbClient(self.mongoHost,
                                                  self.mongoPort,
                                                  self.mongoDb)
        mongoClient.connect()
        collection = mongoClient.getCollection('suites')
        indexes = mongoClient.createIndexModels([("name", ASCENDING),
                                                 ("latest-summary.status", ASCENDING)])
        mongoClient.createIndexes(collection, indexes)
        collection = mongoClient.getCollection('tests')
        indexes = mongoClient.createIndexModels([("name", ASCENDING),
                                                 ("latest-summary.status", ASCENDING)])
        mongoClient.createIndexes(collection, indexes)
        mongoClient.close()

if __name__ == "__main__":

    app = AppMain()
    app.createMongoIndexes()
    appRabbitMQ = app.connectToRabbitMQ()
    appRabbitMQ.connect()
    appRabbitMQ.receive(app.rabbitMQExchange,
                        app.rabbitMQReceiveQueue,
                        app.rabbitMQReceiveRoutingKeys)
    appRabbitMQ.close()
