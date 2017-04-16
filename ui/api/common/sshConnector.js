/*
Author: Madhu Chakravarthy
*/

// Initialize variables

var client = require('ssh2').Client;
var logger = require('./log').logger

var executeCommand = function(cmd, hostname, user, passwd) {

    logger.info("Executing command through ssh")
    var conn = client()
    var result = 'None'
    conn.on('ready', function() {
        logger.debug("Executing command: " + cmd)
        conn.exec(cmd, function(err, stream) {
            if (err) throw err;
            stream.on('close', function(code, signal) {
                logger.debug('Stream :: close :: code: ' + code + ', signal: ' + signal);
                conn.end();
            }).on('data', function(data) {
                logger.debug('STDOUT: ' + data);
                result = data
            }).stderr.on('data', function(data) {
                logger.error('STDERR: ' + data);
                result = data
            });
        });
    logger.info("Finished executing command through ssh")
    }).connect({
        host: hostname,
        port:22,
        username: user, 
        password: passwd 
    });
    return result
}
module.exports.executeCommand = executeCommand 
