/*
Author: Madhu Chakravarthy
*/

// Initialize variables

var moduleName = 'framework1'
var express = require('express')
var router = express.Router()
var config = require('config')
var logger = require('../common/log').logger
var fse =  require('fs-extra')
var path = require('path')
var xml2js = require('xml2js')
var jsonfile = require('jsonfile')

//Initialize xmlparser with attributes

var parser = new xml2js.Parser({"attrkey": "attributes", "trim": true, "charkey": "value"});
var parseString = parser.parseString;

// Functions

var reportParser = function(req, res) {

    var filePath = path.join(process.cwd(), 'reports', 'framework1', 'asterisk-test-suite-report.xml') 
    logger.debug("Report filePath:" + filePath)
    fse.readFile(filePath, 'utf8', function(err, contents) {
        parseString(contents, function(err, result) {
            var suiteList = []
            var suites = result.testsuites.testsuite
            for (i = 0; i < suites.length; i++) {
                suiteList[i] = getSuiteJson(result.testsuites.testsuite[i])
            }
            responseData = {}
            responseData.suites = suiteList
            var response = JSON.stringify(responseData)
            res.end(response)
        })
    })

}

function getSuiteJson(suite) {
    
    logger.info("Building suite json") 
    var suiteName = suite.attributes.name
    var suiteData = {"type": "suite",
                     "name": suiteName,
                     "passed": suite.attributes.passed,
                     "failures": suite.attributes.failures,
                     "skipped": suite.attributes.skipped,
                     "test-ran": suite.attributes.tests,
                     "time-taken": suite.attributes.time,
                     "timestamp": suite.attributes.timestamp
                    }

    suiteData.tests = []
    if ('testcase' in suite) {
        var tests = suite.testcase
        for (var t=0; t < tests.length; t++) {
            suiteData.tests[t] = getTestJson(tests[t], suiteName)
        } 
    }

    return suiteData
}


function getTestJson(test, suiteName) {
    
    logger.info("Building test json") 
    var testName = test.attributes.name
    var testData = {"type": "testcase",
                "name": testName,
                "result": test.attributes.result,
                "time-taken": test.attributes.time
               }

    return testData
}


//All request logger

var requestLogger = function (req, res, next) {
    logger.info('request url received - ', req.url)
    next()
}

router.use(requestLogger)

//Response for test request
router.get('/test', function (req, res) {
    res.send(moduleName + " Test working")
})

//Response for report request
router.get('/reports', function (req, res) {
    reportParser(req, res)
})

module.exports = router
module.exports.moduleName = moduleName
