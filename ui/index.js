/*
Author: Madhu Chakravarthy
*/

// Initialize constants

var express = require('express')
var config = require('config')
var logger = require('./api/common/log').logger
var mongoDb = require('./api/common/mongoClient')
var rabbitMQ = require('./api/common/rabbitMQ')

var app = express()
const port = config.get('server.port')

// Import all framework modules

var frameworkArray = config.get('frameworks')
var frameworkModules = {}
for(var i = 0; length = frameworkArray.length, i < length; i++) {
    var name = frameworkArray[i]
    var module = config.get(name + '.module') 
    var path = './api/' + name + '/' + module + '.js'
    frameworkModules[name] = require(path)
    app.use('/' + name, frameworkModules[name])
    logger.debug("Imported Module: " + frameworkModules[name].moduleName)
}

//Initialize request logger

var requestLogger = function (req, res, next) {
    logger.info('request url received - ', req.url)
    next()
}

app.use(requestLogger)

//Initialize error handler

var errHandler = function (err, req, res, next) {
    console.error(err.stack)
    res.status(500).send('Whoops not a good sign. Something broke')
}

app.use(errHandler)

/*
Routes
*/

//Response for main page 
app.get('/', function (req, res) {
    res.redirect('/dashboard');
})


//Response for dashboard get request
app.get('/dashboard', function (req, res) {
    mongoDb.getDashboardData(req, res)
})

//Response for suite get request
app.get('/suites', function (req, res) {
    mongoDb.getSuitesData(req, res)
})

//Response for test get request
app.get('/tests', function (req, res) {
    mongoDb.getTestsData(req, res)
})

//Response for test start request
app.get('/test/start', function (req, res) {
    rabbitMQ.startTest(req, res)
})

//unsupported URL

app.use(function (req, res, next) {
    res.status(404).send('Page not found')
})
	
//Start the server

app.listen(port, function () {
    mongoDb.createIndex('results')
    console.log('Listening on port: ' + port)
})

