# Author: Madhu Chakravarthy
# Date: 12-04-2017

import os
import json
import paramiko
import logging

#Initialize logger
logger = logging.getLogger('appLogger')

class SSHConnector(object):

    def __init__(self, host):

        logger.info("Initializing SSHConnector for host" + host)
        self.loginDetails = self.readHostInfo(host)
        self.connection = None

    def readHostInfo(self, host):

        logger.debug("Reading " + host + " details")
        filePath = os.path.join(os.getcwd(),'..', 'config', host + '.json')
        with open(filePath) as jsonFile:
            data = json.load(jsonFile)
        return data

    def connectToHost(self):

        logger.debug("Connecting to " + self.loginDetails['host'])
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connection.connect(self.loginDetails['host'],
                                username=self.loginDetails['username'],
                                password=self.loginDetails['password'])

    def executeCommandInHost(self, command):

        if command:
            logger.debug("Executing command in " + self.loginDetails['host'])
            stdin, stdout, stderr = self.connection.exec_command(command)
            stdin.close()
            for line in stdout.read().splitlines():
                logger.debug('%s: %s' % (self.loginDetails['host'], line))
        else:
            logger.debug("Empty command given")

    def copyReportsFromHost(self, source, destination):

        if self.connection:
            logger.debug("Copying file to " + destination)
            sftp = self.connection.open_sftp()
            sftp.get(source, destination)

    def closeConnectionToHost(self):

        if self.connection:
            logger.debug("Closing connection to host " + 
                          self.loginDetails['host'])
            self.connection.close()

if __name__ == "__main__":

    import logging.config

    logging.config.fileConfig(os.path.join(os.getcwd(),'..',
                                          'config', 'logging.conf'))
    logger = logging.getLogger('appLogger')
    logger.info("Started testing SSHConnector")
    
    #sshConn = SSHConnector('10.0.0.3')
    sshConn = SSHConnector('192.168.2.9')
    sshConn.connectToHost()
    sshConn.executeCommandInHost('pybot /home/madhu/robot/demo.robot')
    sshConn.copyReportsFromHost('/home/madhu/robot/output.xml', '../reports/output.xml')
    sshConn.copyReportsFromHost('/home/madhu/robot/log.html', '../reports/log.html')
    sshConn.closeConnectionToHost()
