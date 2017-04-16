// Author: Madhu Chakravarthy
// Date: 14-04-2017

var jsonfile = require('jsonfile')
var testNames1 = ['Lib Test', 'My Test']
var testNames2 = ['SomeTest', 'Bad Test']
var suiteNames = ['Demo', 'Real']
var result = ['PASS', 'FAIL']

function getRandomInt(min, max) {
      return Math.floor(Math.random() * (max - min + 1)) + min;
}

var getValue = function(list) {

    index = getRandomInt(0,1)
    return list[index]

}

var jsonGenerate = function(count) {

    resultArray = []
    for(var i = 0; i <= count; i++) {
        var suiteName = getValue(suiteNames)
        var sampleJson = {
            "name": suiteName,
            "latest-summary": {
                "source": "/home/madhu/robot/" + suiteName + ".robot",
                "status": "PASS",
                "end-time": "20170414 01:28:01.125",
                "start-time": "20170414 01:28:01.094",
                "test-summary": [{
                    "status": getValue(result),
                    "end-time": "20170414 01:28:01.123",
                    "start-time": "20170414 01:28:01.121",
                    "name": getValue(testNames1)
                },
                {
                    "status": getValue(result),
                    "end-time": "20170414 01:28:01.125",
                    "start-time": "20170414 01:28:01.123",
                    "name": getValue(testNames2)
                }]
            }
        }
        var testSummary = sampleJson['latest-summary']['test-summary']
        var test1Result = testSummary[0]['status']
        var test2Result = testSummary[1]['status']
        var suiteResult = 'PASS'
        if(test1Result == 'FAIL' || test2Result == 'FAIL') {
            suiteResult = 'FAIL'
        }
        
        sampleJson['latest-summary']['status'] = suiteResult
        resultArray.push(sampleJson)
    }
    return resultArray
}

function writeToJsonFile(fileName, fileContent) {

    jsonfile.writeFile(fileName, fileContent, {spaces: 4}, function(err) {
         if (err) {
             console.log(err)
         }
    })
}

function writeSampleJsonToFile() {
    writeToJsonFile('./sample.json', {"data": jsonGenerate(50)})
}

writeSampleJsonToFile()
