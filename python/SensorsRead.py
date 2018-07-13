#!/usr/bin/python
#
#  (c) Johan Arens
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
     print "No valid config found"
     exit(1)

print "Will loop every " + str(Refresh) + " sec for 60 sec"
t_end = time.time() + 59


def SensorWorker(SensorName, SensorLocation, SensorAddress, SensorType):
   global SensorReader_Name
   global SensorReader_Location
   global Led_Pin
   global MQTTPublishPath
   global MQTT_Host
   global MQTT_Pass
   global MQTT_Path_Prepend
   global MQTT_Port
   global MQTT_User
   global Refresh

   t_end = time.time() + 59
   while time.time() < t_end:
      current = 1
      GPIO.setwarnings(False)
      GPIO.setmode(GPIO.BCM)

      GPIO.setup(Led_Pin, GPIO.OUT)
      GPIO.output(Led_Pin, True)



      #Turn on the Led
      temperature = 0
      humidity = 0
      SensorType=""
      outputJson=""

      if SensorType == "DHT22":
         ShortSensorType = 22
         try:
            humidity, temperature = Adafruit_DHT.read_retry(ShortSensorType, int(SensorAddress))
         except:
           print "DHT " + int(SensorAddress) + "timeout - no value"

         if humidity is None and temperature is None:
           print "no value returned on dht"
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
         print "Trying 1-wire..."
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
           print "Can't read 1-Wire probe " + SensorAddress + " - Verify config"
         if temperature is None:
           print "no value returned on 1-wire"
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
         GPIO.setup(int(SensorAddress), GPIO.IN, pull_up_down=GPIO.PUD_UP)
         if GPIO.input(int(SensorAddress)):
             DryContact = "OPEN"
         else:
             DryContact = "CLOSED"
         try:
           if int(SensorAddress) < 41:
             GPIO.setup(int(SensorAddress), GPIO.IN, pull_up_down=GPIO.PUD_UP)
             if GPIO.input(SensorAddress):
               DryContact = "OPEN"
             else:
               DryContact = "CLOSED"
         except:
           print "DryContact " + str(SensorAddress) + "timeout - no value"
           DryContact = "Error"
         if DryContact is None:
           print "no value returned on DryContact"
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


          GPIO.output(Led_Pin, False)

          

          GPIO.output(Led_Pin, True)

          print outputJson
          if not MQTT_Path_Prepend.endswith('/'):
            MQTT_Path_Prepend = MQTT_Path_Prepend + "/"
          MQTTPublishPath = MQTT_Path_Prepend   + SensorReader_Name + "/"
          MQTTPublishPath = MQTTPublishPath     + SensorReader_Location + "/"
          MQTTPublishPath = MQTTPublishPath     + SensorName + "/"
          MQTTPublishPath = MQTTPublishPath     + SensorLocation + "/json"

          try:
              if (MQTT_User is not None and MQTT_Pass is not None):
                print "MQTT with auth"
                publish.single(MQTTPublishPath, outputJson, hostname=MQTT_Host, port=MQTT_Port, client_id=SensorReader_Name, transport="tcp", auth = {'username':MQTT_User, 'password':MQTT_Pass}, qos=2)
              else:
                print "MQTT with no auth"
                publish.single(MQTTPublishPath, outputJson, hostname=MQTT_Host, port=MQTT_Port, client_id=SensorReader_Name, transport="tcp", qos=2)
              GPIO.output(Led_Pin, False)
              time.sleep(2)
              GPIO.output(Led_Pin, True)
              time.sleep(2)  
              print "Succefully published to MQTT - Address " + MQTT_Host + ":" + str(MQTT_Port) + " to " + MQTTPublishPath
              GPIO.output(Led_Pin, False)
          except:
              print "Failed to publish to MQTT  - Address " + MQTT_Host + ":" + str(MQTT_Port) + " to " + MQTTPublishPath + " Username/pwd -" + MQTT_User + "-" + MQTT_Pass +"-"
          GPIO.output(Led_Pin, True)
          GPIO.output(Led_Pin, False)
          current +=1
        time.sleep(Refresh)

while current <= len(configReadJson['Sensors']):
    logList = ['Errors and Logs']
    # logList = ["Starting"]
    # logList.append = "Starting ..."
    print "Sensor " + str(current) + " Name: " + configReadJson['Sensors'][str(current)]['Sensor_Name']
    print "Sensor " + str(current) + " Location: " + configReadJson['Sensors'][str(current)]['Sensor_Location']
    print "Sensor " + str(current) + " Address: " + configReadJson['Sensors'][str(current)]['Sensor_Address']
    print "Sensor " + str(current) + " Type: " + configReadJson['Sensors'][str(current)]['Sensor_Type']
    SensorWorker(
        configReadJson['Sensors'][str(current)]['Sensor_Name'],
        configReadJson['Sensors'][str(current)]['Sensor_Location'],
        configReadJson['Sensors'][str(current)]['Sensor_Address'],
        configReadJson['Sensors'][str(current)]['Sensor_Type']
    )