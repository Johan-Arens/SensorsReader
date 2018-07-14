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
import datetime

import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from pprint import pprint

Connected = False   #global variable for the state of the connection

def on_connect(client, userdata, flags, rc):
 
    if rc == 0:
        #print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        print("Connection failed")
 
def on_message(client, userdata, message):
    payloadArray = json.loads(message.payload)
    print "Event time: " + str(datetime.datetime.fromtimestamp(int(payloadArray['Timestamp'])).strftime('%Y-%m-%d %H:%M:%S')) + " - "
    print "Message: "  + message.payload + "<br>"
    


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
#print "<meta http-equiv=\"refresh\" content=\""+ str(Refresh) +"\" >"
print "<meta http-equiv=\"refresh\" content=\"10\" >"
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
          print "   Refresh: " + configReadJson['Sensors'][str(current)]['Sensor_Refresh'] + "<br>"
          print "<hr>"
          current +=1
     print "<form method=\"post\" action=\"/python/config.py\"><button type=\"submit\">Edit Config</button></form>"
     print "<form method=\"post\" action=\"/index.html\"><button type=\"submit\">Stop Debug</button></form>" 
     print "<br><br><br><br>"
     print "<b>MQTT Messages received on Topic: </b>" + MQTT_Path_Prepend + "#<br>"
       

##Client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311, transport="tcp")
#client = mqttClient.Client(client_id="Index_Page" + str(os.getpid()), clean_session=False)
mqtt_clientID="IndexPage"


client = mqttClient.Client(client_id=mqtt_clientID, clean_session=False)
if (MQTT_User is not None and MQTT_Pass is not None):
  client.username_pw_set(MQTT_User, password=MQTT_Pass)  

client.on_connect= on_connect                      
client.on_message= on_message                      

client.connect(MQTT_Host, port=int(MQTT_Port))  
client.loop_start()                        #start the loop

print "<br>"


while Connected != True:    #Wait for connection
    time.sleep(0.1)
 
client.subscribe(MQTT_Path_Prepend + "#", 2)
#client.subscribe("johan/test/single", 2)
#client.subscribe(MQTT_Path_Prepend + "/+", 2)
#client.subscribe("Sensors/SensorsReaderDev2/LabMTL7/Row1_Cold/dht22_17/json", 2)

##try:
##    t_end = time.time() + 15
##
##    while time.time() < t_end:  
##        time.sleep(1)
## 
##except KeyboardInterrupt:
##    print "exiting"
##    client.disconnect()
##    client.loop_stop()






print "</form>"
print "</body>"
print "</html>"
