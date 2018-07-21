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


def SensorWorker(SensorNumber, SensorName, SensorLocation, SensorAddress, SensorType, SensorRefresh):

   global Refresh

   if SensorRefresh != "":
       if SensorRefresh > 0:
           PrintThis("Sensor " + SensorNumber + " " + SensorType + " has different refresh rate")
           ThreadRefresh = SensorRefresh
       else:
           ThreadRefresh = Refresh
   else:
       ThreadRefresh = Refresh
   ThreadRefresh = float(ThreadRefresh)

   PrintThis("Sensor " + SensorNumber + " " + SensorType + " will refresh every " + str(ThreadRefresh))
   t_end = time.time() + 59
   while time.time() < t_end:

      GPIO.setwarnings(False)
      GPIO.setmode(GPIO.BCM)

      GPIO.setup(Led_Pin, GPIO.OUT)
      GPIO.output(Led_Pin, True)



      #Turn on the Led
      temperature = 0
      humidity = 0
      outputJson=""

      if SensorType == "DHT22":
         ShortSensorType = 22
         try:
            humidity, temperature = Adafruit_DHT.read_retry(ShortSensorType, int(SensorAddress))
         except:
             PrintThis("Sensor " + SensorNumber + " " + SensorType + " " + str(SensorAddress) + "timeout - no value")

         if humidity is None and temperature is None:
             PrintThis("Sensor " + SensorNumber + " " + SensorType + " timeout - no value")
         else:
            #print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
            outputJson=json.dumps({
               "Sensor_Name": SensorName,
               "Sensor_Address": SensorAddress,
               "Sensor_Location": SensorLocation,
               "Sensor_Type": SensorType,
               "Temperature": temperature,
               "Humidity": humidity,
               "Timestamp": int(time.time())
            })

      if SensorType == "1-Wire":
         #print "Trying 1-wire..."
         try:
           SensorDataFile = oneWirePath + SensorAddress + "/w1_slave"
           with open(SensorDataFile ,'r') as SensorDataFileRead:
            SensorDataRead = SensorDataFileRead.readlines()
            SensorDataFileRead.close()
            SensorDataReadLines=0
            while SensorDataReadLines < len(SensorDataRead):
              if "t=" in SensorDataRead[SensorDataReadLines]:
                discard, temperature = SensorDataRead[SensorDataReadLines].split("t=")
                temperature = float(temperature) / 1000.0
                break
              SensorDataReadLines += 1

         except:
             PrintThis("Sensor " + SensorNumber + " " + SensorType + str(SensorAddress) + " - timeout - no value")
         if temperature is None:
             PrintThis("Sensor " + SensorNumber + " " + SensorType + str(SensorAddress) + " - timeout - no value")
         else:
            #print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
            outputJson=json.dumps({
               "Sensor_Name": SensorName,
               "Sensor_Address": SensorAddress,
               "Sensor_Location": SensorLocation,
               "Sensor_Type": SensorType,
               "Temperature": temperature,
               "Timestamp": int(time.time())
            })

      if SensorType == "DryContact":
         DryContact = ""

         try:
           if int(SensorAddress) < 41:
             GPIO.setup(int(SensorAddress), GPIO.IN, pull_up_down=GPIO.PUD_UP)
             if GPIO.input(int(SensorAddress)):
               DryContact = "OPEN"
             else:
               DryContact = "CLOSED"
         except:
             PrintThis("Sensor " + SensorNumber + " " + SensorType + str(SensorAddress) + " - timeout - no value")
             DryContact = "Error"
         if DryContact is None:
             PrintThis("Sensor " + SensorNumber + " " + SensorType + str(SensorAddress) + " - timeout - no value")
             DryContact = "Error"
         else:
            #print('Temp={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
            outputJson=json.dumps({
                "Sensor_Name": SensorName,
                "Sensor_Address": SensorAddress,
                "Sensor_Location": SensorLocation,
                "Sensor_Type": SensorType,
                "DryContactStatus": DryContact,
                "Timestamp": int(time.time())
            })

      publishProcess = multiprocessing.Process(target=PublishThis, args=(
             outputJson,
             SensorNumber,
             SensorType,
             SensorName,
             SensorLocation
         ))
      jobs.append(publishProcess)
      publishProcess.start()
      publishProcess.join(timeout=30)


         #PublishThis(outputJson, SensorNumber, SensorType, SensorName, SensorLocation)



      time.sleep(ThreadRefresh)

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
    client_id = SensorReader_Name + SensorNamePub

    try:
        if (MQTT_User is not None and MQTT_Pass is not None):
            #print "MQTT with auth"
            publish.single(MQTTPublishPath, jsonData, hostname=MQTT_Host, port=MQTT_Port, client_id=client_id, transport="tcp", auth={'username': MQTT_User, 'password': MQTT_Pass}, qos=2)
        else:
            #print "MQTT with no auth"
            publish.single(MQTTPublishPath, jsonData, hostname=MQTT_Host, port=MQTT_Port, client_id=client_id, transport="tcp", qos=2)
        GPIO.output(Led_Pin, False)
        time.sleep(2)
        GPIO.output(Led_Pin, True)
        time.sleep(2)
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
            PrintThis(pinfo['name'])
            PrintThis(scriptName[-1])
            if pinfo['name'] == scriptName:
                if pinfo['pid'] == os.getpid():
                    PrintThis("Not Killing myself " + pinfo['pid'])
                PrintThis("Killed process " + pinfo['pid'])
                proc.kill()


CleanUpOldProcess(sys.argv[0])
configOK = False
oneWirePath = "/sys/bus/w1/devices/"

if os.path.exists("/var/www/html/config/config_script.json"):
     with open("/var/www/html/config/config_script.json",'r') as configFileRead:
       configReadJson = configFileRead.read()  
       configFileRead.close()
       configReadJson=json.loads(configReadJson)
       Led_Pin                  = int(configReadJson['Led_Pin'])
       MQTT_Host                = configReadJson['MQTT_Host']
       MQTT_Port                = int(configReadJson['MQTT_Port'])
       MQTT_User                = configReadJson['MQTT_User']
       MQTT_Pass                = configReadJson['MQTT_Pass']
       MQTT_Path_Prepend        = configReadJson['MQTT_Path_Prepend']
       SensorReader_Location    = configReadJson['SensorReader_Location']
       SensorReader_Name        = configReadJson['SensorReader_Name']
       Refresh                  = int(configReadJson['Refresh'])
       SensorTable              = configReadJson
       configOK                 = True
else:
     configOK = False
     
if not configOK:
     PrintThis("No valid config found")
     exit(1)

PrintThis ("Will loop every " + str(Refresh) + " sec for 60 sec")
t_end = time.time() + 59





current = 1
jobs = []
while current <= len(configReadJson['Sensors']):
    logList = ['Errors and Logs']
    # logList = ["Starting"]
    # logList.append = "Starting ..."
    PrintThis( "Sensor " + str(current) + " Name: " + configReadJson['Sensors'][str(current)]['Sensor_Name'])
    PrintThis( "Sensor " + str(current) + " Location: " + configReadJson['Sensors'][str(current)]['Sensor_Location'])
    PrintThis( "Sensor " + str(current) + " Address: " + configReadJson['Sensors'][str(current)]['Sensor_Address'])
    PrintThis( "Sensor " + str(current) + " Type: " + configReadJson['Sensors'][str(current)]['Sensor_Type'])
    PrintThis( "Sensor " + str(current) + " Refresh: " + configReadJson['Sensors'][str(current)]['Sensor_Refresh'])

    p = multiprocessing.Process(target=SensorWorker, args=(
        str(current),
        configReadJson['Sensors'][str(current)]['Sensor_Name'],
        configReadJson['Sensors'][str(current)]['Sensor_Location'],
        configReadJson['Sensors'][str(current)]['Sensor_Address'],
        configReadJson['Sensors'][str(current)]['Sensor_Type'],
        configReadJson['Sensors'][str(current)]['Sensor_Refresh']
    ))
    jobs.append(p)
    p.start()
    current += 1

p.join()
