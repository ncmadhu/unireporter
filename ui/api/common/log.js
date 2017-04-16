/*
Author: Madhu Chakravarthy
*/

const config = require('config')
const winston = require('winston')

var logger = new winston.Logger({
    level: config.get('logger.level'),
    transports: [
        new (winston.transports.Console) ({
            timestamp: function() {
                var d = new Date()
                return d.toUTCString()
            },
            formatter: function(options) {
                return options.timestamp() + ' ' + options.level.toUpperCase() + ' ' +
                       (options.message ? options.message : '')
            },
            handleExceptions: true
        }),
        new (winston.transports.File) ({
            timestamp: function() {
                var d = new Date()
                return d.toUTCString()
            },
            formatter: function(options) {
                return options.timestamp() + ' ' + options.level.toUpperCase() + ' ' +
                       (options.message ? options.message : '')
            },
            handleExceptions: true,
            filename: config.get('logger.logFile')
        })
    ],
    exitOnError: false
})
module.exports.logger = logger
