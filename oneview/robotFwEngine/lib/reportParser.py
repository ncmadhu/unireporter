# Author: Madhu Chakravarthy
# Date: 12-04-2017

import os
import json
import logging
import xmltodict
import mongoDbClient

#Initialize logger
logger = logging.getLogger('appLogger')


class ReportParser(object):

    def __init__(self, fileName, uniqueId, mongoHost, mongoPort, mongoDb):

        logger.info("Initializing parsing of output.xml")
        self.fileName = fileName
        self.uniqueId = uniqueId
        self.mongoHost = mongoHost
        self.mongoPort = mongoPort
        self.mongoDb = mongoDb

    def convertXmlToJson(self):

        logger.debug("Converting xml to json")
        with open(self.fileName, "rb") as f:
            data = xmltodict.parse(f, xml_attribs=True)
            return data

    def parseJsonData(self, data):

        logger.debug("Parsing json data")
        self.dbData = {} 
        suiteData =  data['robot']['suite']
        suiteData = self.parseSuiteData(data['robot']['suite'])
        self.addDataToDatabase()
        self.addDataToFrameworkDb()

    def parseSuiteData(self, suiteData):

        logger.debug("Parsing suite data")

        data = {}
        data['name'] = suiteData['@name']
        data['latest-summary'] = {}
        data['latest-summary']['unique-id'] = self.uniqueId
        data['latest-summary']['source'] = suiteData['@source']
        data['latest-summary']['status'] = suiteData['status']['@status']
        data['latest-summary']['start-time'] = suiteData['status']['@starttime']
        data['latest-summary']['end-time'] = suiteData['status']['@endtime']
        passCount = 0
        failCount = 0
        testSummary = []
        tests = suiteData['test']
        for test in tests:
            testDetail = {}
            testDetail['name'] = test['@name']
            testDetail['status'] = test['status']['@status']
            if testDetail['status'] == 'PASS':
                passCount += 1
            else:
                failCount += 1
            testDetail['start-time'] =  test['status']['@starttime']
            testDetail['end-time'] =  test['status']['@endtime']
            testSummary.append(testDetail)
            testData = self.parseTestData(test, data['name'])
            logger.debug("Test data: " + json.dumps(testData, indent=4))
        data['latest-summary']['test-summary'] = testSummary
        data['latest-summary']['pass'] = passCount 
        data['latest-summary']['fail'] = failCount 
        logger.debug("Update self.dbData for writing to MongoDb")
        self.dbData['suites'] = self.dbData.get('suites', []) + [data]
        logger.debug("Finished parsing suite data")
        return data

    def parseTestData(self, testData, suiteName):

        logger.debug("Parsing test data")

        data = {}
        data['name'] = testData['@name']
        data['Description'] = testData.get('doc', "")
        data['latest-summary'] = {}
        data['latest-summary']['unique-id'] = self.uniqueId
        data['latest-summary']['executed-suite'] = suiteName
        data['latest-summary']['status'] = testData['status']['@status']
        data['latest-summary']['start-time'] = testData['status']['@endtime']
        data['latest-summary']['end-time'] = testData['status']['@starttime']
        keywords = testData['kw']
        keywordSummary = []
        for kw in keywords:
            keywordDetail = {}
            keywordDetail['name'] = kw['@name']
            keywordDetail['library'] = kw.get('@library', '')
            keywordDetail['status'] = kw['status']['@status']
            keywordDetail['start-time'] = kw['status']['@starttime']
            keywordDetail['end-time'] = kw['status']['@endtime']
            keywordSummary.append(keywordDetail)
        data['latest-summary']['keyword-summary'] = keywordSummary
        
        logger.debug("Update self.dbData for writing to MongoDb")
        self.dbData['tests'] = self.dbData.get('tests', []) + [data]
        logger.debug("Finished parsing test data")
        return data

    def writeJsonToFile(self, data):
        
        logger.debug("Writing to output xml to Json file")
        fileName, fileExtension = os.path.splitext(self.fileName)
        fileName = fileName + '.json' 
        data = json.dumps(data, indent=4)
        with open(fileName, 'w') as outFile:
            outFile.write(data)


    def addDataToDatabase(self):

        logger.debug("Adding data to database")
        mongoClient = mongoDbClient.MongoDbClient(self.mongoHost,
                                                  self.mongoPort,
                                                  self.mongoDb)
        mongoClient.connect()
        for key in self.dbData:
            collection = mongoClient.getCollection(key)
            for data in self.dbData[key]:
                mongoClient.addData(collection, data)
        mongoClient.close()


    def addDataToFrameworkDb(self):

        logger.debug("Adding Framework data to database")
        mongoClient = mongoDbClient.MongoDbClient(self.mongoHost,
                                                  self.mongoPort,
                                                  'frameworks')
        mongoClient.connect()
        data = {}
        data['name'] = 'Robot'
        data['suite-name'] = self.dbData['suites'][0]['name']
        data['latest-summary'] = self.dbData['suites'][0]['latest-summary']
        collection = mongoClient.getCollection('results')
        mongoClient.addFrameworkData(collection, data)
        mongoClient.close()


if __name__ == "__main__":

    import logging.config
    logging.config.fileConfig(os.path.join(os.getcwd(),'..',
                                               'config', 'logging.conf'))
    logger.info("Start xml to json test")
    reportParser = ReportParser('../reports/20170414_012800/output.xml')
    data = reportParser.convertXmlToJson()
    reportParser.writeJsonToFile(data)
    reportParser.parseJsonData(json.loads(data))
    logger.info("End xml to json test")




