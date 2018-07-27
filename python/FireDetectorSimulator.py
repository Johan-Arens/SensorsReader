#!/usr/bin/python
#
#  (c) Johan Arens - Cisco Systems
#
#
#

import sys
import Adafruit_DHT
import json
import socket
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import os.path
import RPi.GPIO as GPIO
import time
import multiprocessing
import datetime
import syslog
import sys
import psutil



MQTT_Host                = "10.9.29.116"
MQTT_Port                = 1883
MQTT_User                = None
MQTT_Pass                = None
MQTT_Path_Prepend        = "Sensors/"
MQTTPublishPath          = ''
Refresh = 10
Led_Pin                  = 18
SensorReader_Location    = "Room509"
SensorReader_Name        = "SensorsReaderDev2"

try:
    if sys.argv[1] is not None:
      if sys.argv[1] == "debug":
        printToConsole=True
      else:
        printToConsole=False
    else:
        printToConsole=False
except:
    printToConsole=False

def SimulatorWorker():
    t_end = time.time() + 1000
    global Refresh

    while time.time() < t_end:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(Led_Pin, GPIO.OUT)
        GPIO.output(Led_Pin, True)
        if os.path.exists("/tmp/FireDetected"):
            GPIO.output(Led_Pin, True)
            outputJson = json.dumps({
                "Sensor_Name": 'SC-FD2334-K9',
                "Sensor_Address": "abc-123-abc",
                "Sensor_Location": "Room509",
                "Sensor_Type": "FireDetector",
                "Message": "Fire_Detected",
                "Timestamp": int(time.time())
            })
            PublishThis(outputJson, 1, "FireDetector", "SC-FD2334-K9", "Room509")
            GPIO.output(Led_Pin, False)
        else:
            outputJson = json.dumps({
                "Sensor_Name": 'SC-FD2334-K9',
                "Sensor_Address": "abc-123-abc",
                "Sensor_Location": "Room509",
                "Sensor_Type": "FireDetector",
                "Message": "No_Fire_Detected",
                "Timestamp": int(time.time())
            })
            PublishThis(outputJson, 1, "FireDetector", "SC-FD2334-K9", "Room509")
            GPIO.output(Led_Pin, False)
        if os.path.exists("/tmp/LowBattery"):
            GPIO.output(Led_Pin, True)
            outputJson = json.dumps({
                "Sensor_Name": 'SC-FD2334-K9',
                "Sensor_Address": "abc-123-abc",
                "Sensor_Location": "Room509",
                "Sensor_Type": "FireDetector",
                "Message": "Low_Battery",
                "Battery_Level_Percent": "5",
                "Timestamp": int(time.time())
            })
            PublishThis(outputJson, 1, "FireDetector", "SC-FD2334-K9", "Room509")
            GPIO.output(Led_Pin, False)

        time.sleep(Refresh)

def PrintThis (StringToPrint):
   global printToConsole
   if printToConsole:
      print str(datetime.datetime.now()) + " - " + str(StringToPrint)
   else:
      syslog.syslog(str(StringToPrint))

def PublishThis (jsonData, SensorIndex, SensorTypePub, SensorNamePub, SensorLocationPub):
    global SensorReader_Name
    global SensorReader_Location
    global Led_Pin
    global MQTTPublishPath
    global MQTT_Host
    global MQTT_Pass
    global MQTT_Path_Prepend
    global MQTT_Port
    global MQTT_User
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(Led_Pin, GPIO.OUT)
    GPIO.output(Led_Pin, True)
    GPIO.output(Led_Pin, False)
    GPIO.output(Led_Pin, True)

    if not MQTT_Path_Prepend.endswith('/'):
        MQTT_Path_Prepend = MQTT_Path_Prepend + "/"
    MQTTPublishPath = MQTT_Path_Prepend + SensorReader_Name + "/"
    MQTTPublishPath = MQTTPublishPath + SensorReader_Location + "/"
    MQTTPublishPath = MQTTPublishPath + SensorNamePub + "/"
    MQTTPublishPath = MQTTPublishPath + SensorLocationPub + "/json"
    client_id = SensorReader_Name + MQTTPublishPath.replace ('/', '-')
    #print 'cliend_id is ' + client_id

    try:
        if (MQTT_User is not None and MQTT_Pass is not None):
            #print "MQTT with auth"
            publish.single(MQTTPublishPath, jsonData, hostname=MQTT_Host, port=MQTT_Port, client_id=client_id, transport="tcp", auth={'username': MQTT_User, 'password': MQTT_Pass}, qos=2, keepalive=2)
        else:
            #print "MQTT with no auth"
            publish.single(MQTTPublishPath, jsonData, hostname=MQTT_Host, port=MQTT_Port, client_id=client_id, transport="tcp", qos=2, keepalive=2)
        GPIO.output(Led_Pin, False)
        time.sleep(0.3)
        GPIO.output(Led_Pin, True)
        time.sleep(0.3)
        PrintThis("Sensor " + str(SensorIndex) + " Type: " + str(SensorTypePub) + " SensorData : " + jsonData)
        PrintThis("Sensor " + str(SensorIndex) + " Type: " + str(SensorTypePub) + " Succefully published to MQTT - Address " + MQTT_Host + ":" + str(MQTT_Port) + " to " + MQTTPublishPath)
        GPIO.output(Led_Pin, False)
    except:
        PrintThis("Sensor " + str(SensorIndex) + " Type: " + str(SensorTypePub) + " Failed to publish to MQTT  - Address " + MQTT_Host + ":" + str(MQTT_Port) + " to " + MQTTPublishPath + " Username/pwd -" + str(MQTT_User) + "-" + str(MQTT_Pass) + "-")

    GPIO.output(Led_Pin, True)
    GPIO.output(Led_Pin, False)

def CleanUpOldProcess (scriptName):
    for proc in psutil.process_iter():
        scriptNameLast = scriptName.split('/')
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name'])
        except psutil.NoSuchProcess:
            pass
        else:
            #PrintThis(pinfo['name'])
            #PrintThis(scriptNameLast[-1])
            if pinfo['name'] == scriptNameLast[-1]:
                if pinfo['pid'] == os.getpid():
                    PrintThis("Not Killing myself " + str(pinfo['pid']))
                else:
                    PrintThis("Killed process " + str(pinfo['pid']))
                    proc.kill()



CleanUpOldProcess(sys.argv[0])
configOK = False
oneWirePath = "/sys/bus/w1/devices/"


PrintThis ("Will loop every " + str(Refresh) + " sec for 60 sec")
t_end = time.time() + 59





current = 1
jobs = []

PrintThis( "Sensor " + str(1) + " Name: SC-FD2334-K9")
PrintThis( "Sensor " + str(1) + " Location: Room509")
PrintThis( "Sensor " + str(1) + " Address: abc-123-abc")
PrintThis( "Sensor " + str(1) + " Type: FireDetector")

SimulatorWorker()
