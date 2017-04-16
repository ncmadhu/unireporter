/*
Author: Madhu Chakravarthy
*/

// Initialize variables

var moduleName = 'framework2'
var express = require('express')
var bodyParser = require('body-parser')
var router = express.Router()
var config = require('config')
var logger = require('../common/log').logger
var sshConn = require('../common/sshConnector')
var fse =  require('fs-extra')
var path = require('path')
var xml2js = require('xml2js')
var jsonfile = require('jsonfile')


// create application/json parser
var jsonParser = bodyParser.json()

// create application/x-www-form-urlencoded parser
var urlencodedParser = bodyParser.urlencoded({ extended: false })

//Initialize xmlparser with attributes

var parser = new xml2js.Parser({"attrkey": "attributes", "trim": true, "charkey": "value"});
var parseString = parser.parseString;

//Initialize path variables

var suitePath = path.join(process.cwd(), 'views','data', moduleName, 'suite')
var testPath = path.join(process.cwd(), 'views','data', moduleName, 'test')
var keywordsPath = path.join(process.cwd(), 'views','data', moduleName, 'keyword')

// Functions

function createDataDir(dirList) {

    for (var i = 0; i < dirList.length; i++) {
        var path = dirList[i]
        fse.ensureDir(path, function(err) {
            if (err) {
                logger.error(err)
            }
        })
    }
}

// create data directories if not present
createDataDir([suitePath, testPath, keywordsPath])


function writeToJsonFile(fileName, fileContent) {

    logger.debug("Writing to Json file: " + fileName)
    jsonfile.writeFile(fileName, fileContent, {spaces: 2}, function(err) {
        if (err) {
            logger.error(err)
        }
    })

}

function nameCreator(nameList) {

    var name = ''
    for (var i = 0; i < nameList.length; i++) {
        names = nameList[i].split(' ')
        for (var j = 0; j < names.length; j++) {
            name = name + names[j].substr(0,3)
        }
    }
    return name
}

var reportParser = function(req, res) {

    var filePath = path.join(process.cwd(), 'reports', 'framework2', 'output.xml') 
    logger.debug("filePath:" + filePath)
    fse.readFile(filePath, 'utf8', function(err, contents) {
        parseString(contents, function(err, result) {
            var suiteList = []
            var suites = result.robot.suite
            for (i = 0; i < suites.length; i++) {
                suiteList[i] = writeSuiteJsonFile(result.robot.suite[i])
            }
            responseData = {}
            responseData.suites = suiteList
            responseData.statistics = result.robot.statistics[0].total[0].stat
            responseData.suitestats = result.robot.statistics[0].suite[0].stat
            responseData.tags = result.robot.statistics[0].tag[0].stat
            responseData.errors = result.robot.errors
            var response = JSON.stringify(responseData)
            res.end(response)
        })
    })

}

function writeSuiteJsonFile(suite) {
    
    logger.info("Building suite json") 
    var suiteName = suite.attributes.name
    var suiteData = {"type": "suite",
                     "name": suiteName,
                     "status": suite.status[0].attributes.status
                    }

    suiteData.keywords = []
    if ('kw' in suite) {
        var keywords = suite.kw
        var rootName = nameCreator([suiteName])
        for (var k=0; k < keywords.length; k++) {
            suiteData.keywords[k] =  writeKeywordJsonFile(keywords[k], suiteName, rootName)
        }
    }

    suiteData.tests = []
    if ('test' in suite) {
        var tests = suite.test
        for (var t=0; t < tests.length; t++) {
            suiteData.tests[t] = writeTestJsonFile(tests[t], suiteName)
        } 
    }

    var suiteFile = path.join(suitePath, suiteName.replace(/ /g, '_') + '.json')
    writeToJsonFile(suiteFile.toLowerCase(), suiteData)
    return suiteName
}


function writeTestJsonFile(test, suiteName) {
    
    logger.info("Building test json") 
    var testName = test.attributes.name
    var testData = {"type": "testcase",
                "name": testName,
                "executedBy": suiteName,
                "status": test.status[0].attributes.status,
                "starttime": test.status[0].attributes.starttime,
                "endtime": test.status[0].attributes.endtime,
                "critical": test.status[0].attributes.critical,
                "tags": test.tags[0].tag
               }

    testData.keywords = []
    if ('kw' in test) {
        var keywords = test.kw
        var rootName = nameCreator([suiteName, testName])
        for (var k=0; k < keywords.length; k++) {
            testData.keywords[k] =  writeKeywordJsonFile(keywords[k], testName, rootName)
        }
    }

    var parentName = nameCreator([suiteName])
    var testFile = path.join(testPath, parentName + '_' + testName.replace(/ /g, '_') + '.json')
    writeToJsonFile(testFile.toLowerCase(), testData)
    return testName
    
}

function writeKeywordJsonFile(keyword, parent, rootName) {
   
    logger.info("Building Keyword Json")
    var data = {}
    var attributes = keyword.attributes
    var keywordName = attributes.name
    data.name = keywordName
    data.executedBy = parent
    data.type = attributes.type || 'NA'
    data.library = attributes.library || 'NA'

    data.description = 'NA'
    if ('doc' in keyword) {
        data.description = keyword.doc[0]
    }

    data.arguments = []
    if ('arguments' in keyword) {
        data.arguments = keyword.arguments[0].arg
    }
        
    data.logMessages = []
    if ('msg' in keyword) {
      logMessages = keyword.msg
      for (var i=0; i < logMessages.length; i++) {
          data.logMessages[i] = logMessages[i].value
      } 
    }
    
    var status = keyword.status[0]
    data.status = status.attributes.status
    data.starttime = status.attributes.starttime
    data.endtime = status.attributes.endtime
    data.keywords = []
    
    if ('kw' in keyword) {
        var childKeywords = keyword.kw
        var keyWordRootName = rootName + '_' + nameCreator(keywordName)
        for (var k=0; k < childKeywords.length; k++) {
            data.keywords.push(writeKeywordJsonFile(childKeywords[k], keywordName, keyWordRootName))
        }
    }
    
    var keywordFile = path.join(keywordsPath, rootName + '_' + data.name.replace(/ /g, '_')  + '.json')
    writeToJsonFile(keywordFile.toLowerCase(), data)
    return data.name 
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

//Response for test execute 
router.post('/test/execute', jsonParser, function (req, res) {

    var filePath = path.join(process.cwd(), 'config', req.body.host + ".json")
    jsonfile.readFile(filePath, function(err, obj) {
         logger.debug("command " + req.body.command)
         var result = sshConn.executeCommand(req.body.command, obj.host, obj.username, obj.password)
         res.send("Command executed on " + obj.host)
    })

})


//Response for add executor 
router.post('/add/executor', jsonParser, function (req, res) {

    var filePath = path.join(process.cwd(), 'config', req.body.host + ".json") 
    writeToJsonFile(filePath.toLowerCase(), req.body)
    res.send("Added test executor " + req.body.host +" for " + moduleName)

})
module.exports = router
module.exports.moduleName = moduleName
