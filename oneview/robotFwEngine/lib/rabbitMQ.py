# Author: Madhu Chakravarthy
# Date: 12-04-2017

import pika
import logging
import taskExecutor

#Initialize logger
logger = logging.getLogger('appLogger')


class RabbitMQ(object):

    def __init__(self, host, port, user, password):

        logger.debug("Initializing RabbitMQ")
        self.connection = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.credentials = pika.PlainCredentials(self.user, self.password)
        self.taskExecutor = taskExecutor.TaskExecutor() 
        logger.debug("Initialized RabbitMQ")

    def connect(self):
   
        logger.debug("Establishing connection to the host: " + self.host)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                                                  host=self.host,
                                                  port=self.port,
                                                  credentials=self.credentials))

    def close(self):

        self.connection.close()
        logger.debug("Closed connection to the host: " + self.host)

    def exchangeDeclare(self, exchange):

        channel = self.connection.channel()
        channel.exchange_declare(exchange=exchange, type='direct')
        logger.debug("Declared Exchange: " + exchange)
        return channel

    def queueDeclare(self, channel, queueName):

        channel.queue_declare(queue=queueName, durable=True, auto_delete=True)
        logger.debug("Declared queue: " + queueName)
        return channel

    def receiveCallback(self, ch, method, properties, body):

        logger.debug("Received message: " + body)
        logger.debug("Routing Key: " + method.routing_key)
        self.taskExecutor.executeTask(method.routing_key, body)
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def receive(self, exchange, queueName, receiveRoutingKeys):

        channel = self.exchangeDeclare(exchange)
        channel = self.queueDeclare(channel, queueName)
        for key in receiveRoutingKeys:
            channel.queue_bind(exchange=exchange,
                               queue=queueName,
                               routing_key=key)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.receiveCallback, queue=queueName)
        logger.info("Waiting for task in queue: " + queueName)
        channel.start_consuming()

    def send(self, exchange='', routingKey='status', message=None):

        if message:
            channel = self.exchangeDeclare(exchange)
            channel.basic_publish(exchange=exchange,
                                  routing_key=routingKey,
                                  body=message,
                                  properties=pika.BasicProperties(
                                      delivery_mode = 2,
                                  ))
            logger.info("Published Message to the: " + routingKey)

if __name__ == "__main__":

    logger.info("Testing Send start")
    routingKeys = [['start', '{"host": "192.168.2.9",\
                               "test-suite": "/home/madhu/robot/demo.robot"}'],
                   ['stop', 'testBody'],
                   ['status', 'testBody'],
                   ['addHost', '{"host":"10.0.0.4",\
                                "username": "madhu",\
                                "password": "calsoftlabs"}']]
    rabbit = RabbitMQ('localhost', 5672, 'oneview', 'oneview')
    rabbit.connect()
    for keyValue in routingKeys:
        message = keyValue[1]
        rabbit.send('robot', keyValue[0], message)
    rabbit.close()
    logger.info("Testing Send end")
