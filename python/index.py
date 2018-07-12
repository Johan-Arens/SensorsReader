#!/usr/bin/env python
# -*- coding: UTF-8 -*-# enable debugging
import cgitb
import cgi
import socket
import json
import os.path
import os
import Adafruit_DHT
import RPi.GPIO as GPIO
#import paho.mqtt.publish as publish
import paho.mqtt.client as mqttClient
import time

import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

Connected = False   #global variable for the state of the connection

def on_connect(client, userdata, flags, rc):
 
    if rc == 0:
        #print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        print("Connection failed")
 
def on_message(client, userdata, message):
    print "Message received: "  + message.payload + "<br>"

configOK = False




if os.path.exists("/var/www/html/config/config_script.json"):
     with open("/var/www/html/config/config_script.json",'r') as configFileRead:
       configReadJson = configFileRead.read()  
       configFileRead.close()
       configReadJson=json.loads(configReadJson)
       Led_Pin                     = int(configReadJson['Led_Pin'])
       MQTT_Host                   = configReadJson['MQTT_Host']
       MQTT_Port                   = configReadJson['MQTT_Port']
       MQTT_User                   = configReadJson['MQTT_User']
       MQTT_Pass                   = configReadJson['MQTT_Pass']
       Refresh                     = int(configReadJson['Refresh'])
       MQTT_Path_Prepend           = configReadJson['MQTT_Path_Prepend']
       SensorReader_Location       = configReadJson['SensorReader_Location']
       SensorReader_Name           = configReadJson['SensorReader_Name']
       configOK          = True

print("Content-Type: text/html;charset=utf-8")
print("")

print "<html>"
print "<head>"

print "<meta http-equiv=\"refresh\" content=\"20\" >"
print "</head>"
print "<title>Sensor Reader</title>"

print "<body>"

if not configOK:
     print "Sensor not yet configured<br>"
     print "<form method=\"post\" action=\"/python/config.py\"><button type=\"submit\">Create Config</button></form>"

else:
     print "<b>Sensor Reader</b> : " + SensorReader_Name + "<br>"
     print "<b>Sensor Location</b> : " + SensorReader_Location + "<br>"
     print "<b>Script Refresh : </b>" + str(Refresh) + " sec<br>"
     print "<b>MQTT Host : </b>" + MQTT_Host + " <br>"
     print "<b>MQTT Port : </b>" + MQTT_Port + " <br>"
     print "<b>MQTT Topic Prepend : </b>" + MQTT_Path_Prepend + " <br>"
     if MQTT_User is not None:
       print "<b>MQTT user : </b>" + MQTT_User + " <br>"
     else:
       print "<b>MQTT user : </b>None<br>"
     if MQTT_Pass is not None:
       print "<b>MQTT Pass : </b>******<br>"
     else:
       print "<b>MQTT Pass : </b>None<br>"
     print "Script pid is " +  str(os.getpid()) + "<br>"
     
     current = 1
     print "<hr>"
     while current <= len(configReadJson['Sensors']):
          print "<b>Sensor " + str(current) + "</b><br>"
          print "Name: " + configReadJson['Sensors'][str(current)]['Sensor_Name'] + "<br>"
          print "   Location: " + configReadJson['Sensors'][str(current)]['Sensor_Location'] + "<br>"
          print "   Address: " + configReadJson['Sensors'][str(current)]['Sensor_Address'] + "<br>"
          print "   Type: " + configReadJson['Sensors'][str(current)]['Sensor_Type'] + "<br>"
          print "<hr>"
          current +=1
     print "<form method=\"post\" action=\"/python/config.py\"><button type=\"submit\">Edit Config</button></form>"
     print "<form method=\"post\" action=\"/python/indexMQTTread.py/\"><button type=\"submit\">Debug Sensors</button></form>"  

print "</form>"
print "<hr>"
print "<h3>Roadmap</h3>"
print "<form action=\"/action_page.php\">"
print  "<input type=\"checkbox\" name=\"\" value=\"\">MQTT Encryption<br>"
print  "<input type=\"checkbox\" name=\"\" value=\"\">MQTT Encryption onboarding (certificates autogen)<br>"
print  "<input type=\"checkbox\" name=\"\" value=\"\">Authentication<br>"
print  "<input type=\"checkbox\" checked name=\"\" value=\"\">1-Wire Sensors support<br>"
print  "<input type=\"checkbox\" name=\"\" value=\"\">Dynamic sensors nubmer in config section, currently 7 are hardcoded<br>"
print  "<input type=\"checkbox\" name=\"\" value=\"\">Cosmetic, at this point, there is none...<br>"  
print "</form>"
print "</body>"
print "</html>"
