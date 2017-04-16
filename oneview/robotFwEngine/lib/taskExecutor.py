# Author: Madhu Chakravarthy
# Date: 12-04-2017

import os
import json 
import logging
import sshConnector
import reportParser
import ConfigParser
from datetime import datetime

#Initialize logger
logger = logging.getLogger('appLogger')

class TaskExecutor(object):

    def __init__(self):

        logger.debug("Initializing task executor")

        self.tasks = {"start": self.taskStart,
                      "stop": self.taskStop,
                      "status": self.taskStatus,
                      "addHost": self.taskAddHost}

        self.config = self.loadConfig()
        self.initMongoDbConfig()
        reportFiles = self.config.get('ReportFiles', 'files')
        self.reportFiles = reportFiles.split(',') 
        self.transport = self.config.get('Executor', 'transport')

    def taskStart(self,body):

        logger.info("Executing start")
        if body:
            data = json.loads(body)
            host = data['host']
            testSuite = data['test-suite']
            uniqueId = self.generateUniqueId()
            sourceDir = os.path.join('/', 'tmp', uniqueId)
            destDir = os.path.join(os.getcwd(), '..', 'reports', uniqueId)
            cmd = self.commandGenerator(testSuite, sourceDir)

            if self.transport == 'ssh':
                self.startTaskInSSH(host, cmd, sourceDir, destDir)
            parser = reportParser.ReportParser(os.path.join(destDir,
                                               'output.xml'),
                                               uniqueId,
                                               self.mongoHost,
                                               self.mongoPort,
                                               self.mongoDb)
            data = parser.convertXmlToJson()
            parser.parseJsonData(data)
            parser.writeJsonToFile(data)


    def startTaskInSSH(self, host, cmd, sourceDir, destDir):

        sshConn = sshConnector.SSHConnector(host)
        sshConn.connectToHost()
        sshConn.executeCommandInHost(cmd)
        self.copyReportFilesInSSH(sshConn, sourceDir, destDir)
        sshConn.closeConnectionToHost()

    def taskStop(self,body):

        logger.info("Executing stop")

    def taskStatus(self,body):

        logger.info("Executing status")

    def taskAddHost(self,body):

        logger.info("Executing task addHost")
        if body:
            data = json.loads(body)
            host = data['host']
            filePath = os.path.join(os.getcwd(),'..', 'config', host + '.json')
            with open(filePath, 'w') as outFile:
                json.dump(data, outFile, indent=4)
            logger.debug("Written " + host + " info to file " + host + ".json")

    def executeTask(self, task, body):

        logger.debug("Received task: " +  task)
        self.tasks[task](body)

    def copyReportFilesInSSH(self, sshConn, sourceDir, destDir):

        logger.debug("Copying report files")
        os.mkdir(destDir)
        for reportFile in self.reportFiles:
            sourceFile = os.path.join(sourceDir, reportFile)
            destFile = os.path.join(destDir, reportFile)
            sshConn.copyReportsFromHost(sourceFile, destFile)

    def commandGenerator(self, testSuite, outputDir):

        uniqueId = self.generateUniqueId
        cmd = "pybot --outputdir " + outputDir + " " + testSuite
        return cmd

    def generateUniqueId(self):

        logger.debug("Generating unique Id")
        now = datetime.now()
        date = datetime.date(now)
        time = datetime.time(now)
        uniqueId = "{year}{month:02}{day:02}_{hour:02}{minute:02}{second:02}"\
                    .format(year=date.year,
                            month=date.month,
                            day=date.day,
                            hour=time.hour,
                            minute=time.minute,
                            second=time.second)
        return uniqueId


    def loadConfig(self):

        logger.debug("Loading configuration")
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(os.getcwd(), '..', 'config', 'config.ini'))
        logger.debug("Config Sections: " + str(config.sections()))
        return config

    def initMongoDbConfig(self):

        logger.debug("Initializing MongoDb config")
        self.mongoHost = self.config.get('MongoDB', 'host')
        self.mongoPort = self.config.get('MongoDB', 'port')
        self.mongoDb = self.config.get('MongoDB', 'database')



if __name__ == "__main__":

    import logging.config

    logging.config.fileConfig(os.path.join(os.getcwd(),'..',
                                           'config', 'logging.conf'))
    logger = logging.getLogger('appLogger')
    logger.info("Started testing TaskExecutor")
    taskExec = TaskExecutor()
    taskExec.executeTask("addHost", json.dumps({"host": "10.0.0.3",
                                                "username": "madhu",
                                                "password": "calsoftlabs"}))
    logger.info("Finished testing TaskExecutor")
