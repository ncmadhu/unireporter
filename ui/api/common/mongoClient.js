/*
Author: Madhu Chakravarthy
*/

// Initialize variables

var config = require('config')
var logger = require('./log').logger
var assert = require('assert')
var mongoClient = require('mongodb').MongoClient;
var mongoDbHost = config.get('mongodb.host')
var mongoDbPort = config.get('mongodb.port')
var urlPrefix = 'mongodb://' + mongoDbHost + ':' + mongoDbPort + '/'

var connectAndFetch = function(err, db, collection, req, res) {
    assert.equal(null, err)
    logger.info("Connected to database successfully")
    findDocument(db, collection, req, res)
    db.close()
}

var getDashboardData = function(req, res) {

    logger.info("Getting Dashboard data")

    // Connection URL 
    var url = urlPrefix + 'frameworks'
    mongoClient.connect(url, function(err, db) {
        connectAndFetch(err, db, 'results', req, res)
    })
}

var getSuitesData = function(req, res) {

    logger.info("Getting suite data")
    var database = req.query.framework
    // connection URL
    var url = urlPrefix + database
    mongoClient.connect(url, function(err, db) {
        connectAndFetch(err, db, 'suites', req, res)
    })
}

var getTestsData = function(req, res) {

    logger.info("Getting test data")
    var database = req.query.framework
    // connection URL
    var url = urlPrefix + database
    mongoClient.connect(url, function(err, db) {
        connectAndFetch(err, db, 'tests', req, res)
    })
}

var findDocument = function(db, collctn, req, res) {

    logger.debug("Finding document in collection")
    var collection = db.collection(collctn)

    // send query params in actual object format
    // with key as query. example below
    // query={"name": "Robot","latest-summary.status": "FAIL"}
    // projection={"_id": 0, "latest-summary.status": 1}
    // framework=robot

    var queryParams = {}
    if(req.query.query) {
        queryParams = JSON.parse(req.query.query)
    }

    var projectionParams = {}
    if(req.query.projection) {
        projectionParams = JSON.parse(req.query.projection)
    }
     
    docs = collection.find(queryParams, projectionParams).toArray(function(err, docs) {
        if (docs) {
            res.status(200).json({'results' : docs})
        } else {
            res.status(200).json({'results': {}})
            assert.equal(null, err);
        }
    })
}

var createIndex = function(collection) {

    logger.info("Creating Index in DB")

    // Connection URL 
    var url = urlPrefix + 'frameworks'
    mongoClient.connect(url, function(err, db) {
        if(err) {
            logger.debug("Not able to create index")
        } else {
            db.createIndex(collection, {name: 1},
                           {unique:true}, function(err, indexName) {
                logger.debug("Created index")
                db.close()
            })
        }
    })
}

module.exports = {
    getDashboardData: getDashboardData,
    getSuitesData: getSuitesData,
    getTestsData: getTestsData,
    createIndex: createIndex
}
