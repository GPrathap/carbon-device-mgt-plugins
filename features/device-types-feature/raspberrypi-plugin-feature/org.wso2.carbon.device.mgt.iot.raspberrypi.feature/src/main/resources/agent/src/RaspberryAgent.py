#!/usr/bin python
"""
/**
* Copyright (c) 2015, WSO2 Inc. (http://www.wso2.org) All Rights Reserved.
*
* WSO2 Inc. licenses this file to you under the Apache License,
* Version 2.0 (the "License"); you may not use this file except
* in compliance with the License.
* You may obtain a copy of the License at
*
* http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an
* "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
* KIND, either express or implied. See the License for the
* specific language governing permissions and limitations
* under the License.
**/
"""

import logging, logging.handlers
import sys, os, signal, argparse
import running_mode
import time, threading, datetime, calendar
import iotUtils, mqttConnector, httpServer

PUSH_INTERVAL = 2  # time interval between successive data pushes in seconds


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       Logger defaults
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
LOG_FILENAME = "RaspberryStats.log"
logging_enabled = False
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       Python version
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if sys.version_info<(2,7,0):
    sys.stderr.write("You need python 2.7.0 or later to run this script\n")
    exit(1)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       Define and parse command line arguments
#       If the log file is specified on the command line then override the default
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
parser = argparse.ArgumentParser(description="Python service to push RPi info to the Device Cloud")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")

help_string_for_data_push_interval = "time interval between successive data pushes (default '" + str(PUSH_INTERVAL) + "')"
help_string_for_running_mode = "where is going to run on the real device or not"
parser.add_argument("-i", "--interval", type=int, help=help_string_for_data_push_interval)
parser.add_argument("-m", "--mode", type=str, help=help_string_for_running_mode)

args = parser.parse_args()
if args.log:
    LOG_FILENAME = args.log

if args.interval:
    PUSH_INTERVAL = args.interval

if args.mode:
    running_mode.RUNNING_MODE = args.mode
    iotUtils = __import__('iotUtils')
    mqttConnector = __import__('mqttConnector')
    httpServer = __import__('httpServer') # python script used to start a http-server to listen for operations
    # (includes the TEMPERATURE global variable)

    if running_mode.RUNNING_MODE == 'N':
        Adafruit_DHT = __import__('Adafruit_DHT') # Adafruit library required for temperature sensing
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       A class we can use to capture stdout and sterr in the log
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class IOTLogger(object):
    def __init__(self, logger, level):
        """Needs a logger and a logger level."""
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.rstrip() != "":  # Only log if there is a message (not just a new line)
            self.logger.log(self.level, message.rstrip())
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       Configure logging to log to a file,
#               making a new file at midnight and keeping the last 3 day's data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def configureLogger(loggerName):
    logger = logging.getLogger(loggerName)
    logger.setLevel(LOG_LEVEL)  # Set the log level to LOG_LEVEL
    handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight",
                                                        backupCount=3)  # Handler that writes to a file,
    # ~~~make new file at midnight and keep 3 backups
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')  # Format each log message like this
    handler.setFormatter(formatter)  # Attach the formatter to the handler
    logger.addHandler(handler)  # Attach the handler to the logger

    if (logging_enabled):
        sys.stdout = IOTLogger(logger, logging.INFO)  # Replace stdout with logging to file at INFO level
        sys.stderr = IOTLogger(logger, logging.ERROR)  # Replace stderr with logging to file at ERROR level
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       This method registers the DevieIP in the Device-Cloud
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# def registerDeviceIP():
#     ssl.wrap_socket = sslwrap(ssl.wrap_socket) # using the overridden sslwrap that uses TLSv1
#     if sys.version_info<(2,7,9):
#         dcConncection = httplib.HTTPSConnection(host=DC_IP, port=DC_PORT)
#     else:
#         dcConncection = httplib.HTTPSConnection(host=DC_IP, port=DC_PORT, context=ssl._create_unverified_context())
#     #TODO need to get server certificate when initializing https connection
#     dcConncection.set_debuglevel(1)
#     dcConncection.connect()
#
#     registerURL = str(REGISTER_ENDPOINT) + '/' + str(iotUtils.DEVICE_OWNER) + '/' + str(iotUtils.DEVICE_ID) + '/' + \
#                   str(HOST) + '/' + str(HOST_HTTP_SERVER_PORT) + '/'
#     dcConncection.putrequest('POST', registerURL)
#     dcConncection.putheader('Authorization', 'Bearer ' + iotUtils.AUTH_TOKEN)
#     dcConncection.endheaders()
#     dcResponse = dcConncection.getresponse()
#
#     print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
#     print ('RASPBERRY_STATS: ' + str(registerURL))
#     print ('RASPBERRY_STATS: ' + str(dcResponse.status))
#     print ('RASPBERRY_STATS: ' + str(dcResponse.reason))
#     print ('RASPBERRY_STATS: Response Message')
#     print str(dcResponse.msg)
#
#     dcConncection.close()
#     print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def connectAndPushDataBrainInfo():
    currentTime = calendar.timegm(time.gmtime())
    PUSH_DATA_BRAIN_WAVE_INFO = iotUtils.BRAIN_WAVE_INFO.format(currentTime, 0.0, 0.0, 0.0, 0.0,  0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    print '~~~~~~~~~~~~~~~~~~~~~~~~ Publishing Device-Data ~~~~~~~~~~~~~~~~~~~~~~~~~'
    print ('PUBLISHED DATA: ' + PUSH_DATA_BRAIN_WAVE_INFO)
    print ('PUBLISHED TOPIC: ' + mqttConnector.TOPIC_TO_PUBLISH_BRAIN_WAVE_INFO)
    mqttConnector.publish(PUSH_DATA_BRAIN_WAVE_INFO)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       This is a Thread object for reading temperature continuously
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class BrainWaveReadingThread(object):
    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def run(self):

        # Try to grab a sensor reading.  Use the read_retry method which will retry up
        # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
        while True:
            try:
                connectAndPushDataBrainInfo()
            except Exception, e:
                print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
                print "RASPBERRY_STATS: Exception in TempReaderThread: Could not successfully read Temperature"
                print ("RASPBERRY_STATS: " + str(e))                
                pass
                time.sleep(20)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       This is a Thread object for listening for MQTT Messages
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class UtilsThread(object):
    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def run(self):
        iotUtils.main()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       This is a Thread object for HTTP-Server that listens for operations on RPi
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class ListenHTTPServerThread(object):
    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def run(self):
        httpServer.main()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       This is a Thread object for connecting and subscribing to an MQTT Queue
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SubscribeToMQTTQueue(object):
    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def run(self):
        mqttConnector.main()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       When sysvinit sends the TERM signal, cleanup before exiting
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def sigterm_handler(_signo, _stack_frame):
    print("[] received signal {}, exiting...".format(_signo))
    sys.exit(0)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


signal.signal(signal.SIGTERM, sigterm_handler)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       The Main method of the RPi Agent
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    configureLogger("WSO2IOT_RPiStats")
    UtilsThread()
    # registerDeviceIP()  # Call the register endpoint and register Device IP
    # ListenHTTPServerThread()  # starts an HTTP Server that listens for operational commands to switch ON/OFF Led
    SubscribeToMQTTQueue()  # connects and subscribes to an MQTT Queue that receives MQTT commands from the server
    BrainWaveReadingThread()  # initiates and runs the thread to continuously read temperature from DHT Sensor
    # time.sleep(2) #wait for agent to connect to broker before publishing data
    while True:
        try:

            # if iotUtils.LAST_TEMP > 0:  # Push data only if there had been a successful temperature read
            #     connectAndPushData()  # Push Sensor (Temperature) data to WSO2 BAM
            time.sleep(60)
        except (KeyboardInterrupt, Exception) as e:
            print "RASPBERRY_STATS: Exception in RaspberryAgentThread (either KeyboardInterrupt or Other)"
            print ("RASPBERRY_STATS: " + str(e))
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            pass
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


if __name__ == "__main__":
    main()
