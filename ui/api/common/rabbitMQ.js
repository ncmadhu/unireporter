/*
Author: Madhu Chakravarthy
*/

// Initialize variables

var config = require('config')
var logger = require('./log').logger
var path = require('path')
var jsonfile = require('jsonfile')
var amqp = require('amqplib/callback_api')
var rabbitMQHost = config.get('rabbitmq.host')
var rabbitMQPort = config.get('rabbitmq.port')
var rabbitMQUser = config.get('rabbitmq.username')
var rabbitMQPassword = config.get('rabbitmq.password')
var rabbitMQSendQueue = config.get('rabbitmq.sendqueue')

// connection URL

var url = 'amqp://' + rabbitMQUser + ':' + rabbitMQPassword + 
          '@' + rabbitMQHost + ':' + rabbitMQPort

var sendMessage = function(exchange, routingKey, message) {

    logger.info("Sending message through rabbitMQ")
    amqp.connect(url, function(err, conn) {
        conn.createChannel(function(err, ch) {
            ch.assertExchange(exchange, 'direct', {durable: false})
            ch.publish(exchange, routingKey, new Buffer(message),
                      {deliveryMode: 2})
            logger.debug("Sent Message " + message)
        })
        setTimeout(function() { conn.close() }, 500)
    })
}

var startTest = function(req, res){

    logger.debug("Starting test")
    var filePath = path.join(process.cwd(), 'config', "sampleTestStart.json")
    logger.info("MQ:" + filePath)
    jsonfile.readFile(filePath, function(err, obj) {
        var result = sendMessage(obj.exchange, obj.routingKey,
                                 JSON.stringify(obj)) 
        logger.debug(JSON.stringify(obj))
        res.send("Test started on host " + obj.host)
    })
}

module.exports = {
    sendMessage: sendMessage,
    startTest: startTest
}
