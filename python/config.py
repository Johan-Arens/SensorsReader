#!/usr/bin/env python
# -*- coding: UTF-8 -*-# enable debugging
import cgitb
import cgi
import socket
import json
import os.path
from os import listdir
from os.path import isfile, join

cgitb.enable()

form = cgi.FieldStorage() 

NewConfig = form.getvalue('NewConfig')


if bool(NewConfig) is True:
  
  print "Content-Type: text/html;charset=utf-8"
  print ""
  print "<html>"
  print "<head>"
  print "<meta http-equiv=\"refresh\" content=\"3;url=/python/config.py\" />"
  print "<title>Sensor Config Saving</title>"
  print "</head>"
  
  # Get data from fields
  SensorReader_Name         = form.getvalue('SensorReader_Name')
  SensorReader_Location     = form.getvalue('SensorReader_Location')
  MQTT_Host                 = form.getvalue('MQTT_Host')
  MQTT_Port                 = form.getvalue('MQTT_Port')
  MQTT_User                 = form.getvalue('MQTT_User')
  MQTT_Pass                 = form.getvalue('MQTT_Pass')
  GPIO_Pin                  = form.getvalue('GPIO_Pin')
  Sensor_Type               = form.getvalue('Sensor_Type')
  Led_Pin                   = form.getvalue('Led_Pin')
  Refresh                   = form.getvalue('Refresh')
  MQTT_Path_Prepend         = form.getvalue('MQTT_Path_Prepend')
  MQTT_User                 = form.getvalue('MQTT_User')
  MQTT_Pass                 = form.getvalue('MQTT_Pass')
  Sensors                   = form.getvalue('Sensors')
  configOK = True
  
  ConfigDict=({
      "SensorReader_Name": SensorReader_Name,
      "SensorReader_Location": SensorReader_Location,
      "MQTT_Host": MQTT_Host,
      "MQTT_Port": MQTT_Port,
      "MQTT_User": MQTT_User,
      "MQTT_Pass": MQTT_Pass,
      "Led_Pin": Led_Pin,
      "Refresh": Refresh,
      "MQTT_Path_Prepend": MQTT_Path_Prepend      
   })

  # Extracting data from the form and saving it
  stop = False
  SensorNumber = 1
  ConfigDict['Sensors']={}
  while stop is False:
    if form.getvalue('Sensors[' + str(SensorNumber) +'][Sensor_Location]') is not None:
      ConfigDict['Sensors'][SensorNumber]={}
      ConfigDict['Sensors'][SensorNumber]['Sensor_Name']      = form.getvalue('Sensors[' + str(SensorNumber) +'][Sensor_Name]')
      ConfigDict['Sensors'][SensorNumber]['Sensor_Location']  = form.getvalue('Sensors[' + str(SensorNumber) +'][Sensor_Location]')
      ConfigDict['Sensors'][SensorNumber]['Sensor_Address']   = form.getvalue('Sensors[' + str(SensorNumber) +'][Sensor_Address]')
      ConfigDict['Sensors'][SensorNumber]['Sensor_Type']      = form.getvalue('Sensors[' + str(SensorNumber) +'][Sensor_Type]')
      ConfigDict['Sensors'][SensorNumber]['Sensor_Refresh']   = form.getvalue('Sensors[' + str(SensorNumber) +'][Sensor_Refresh]')
    else:
       stop = True
    SensorNumber += 1
  
  ConfigJson=json.dumps(ConfigDict)
  if configOK:
     try:
        with open("/var/www/html/config/config_script.json",'w') as configFileWrite:
          configFileWrite.write(ConfigJson)
     finally:
        configFileWrite.close()

  configReadJson = ""
  
  
  print "<body>"
  print "<center><div style=\"width:500px;height:100px;border:1px solid #000;\"><center><b>Config Saved !</center></b></div></center>"
  
  print "</body>"
  print "</html>"
  exit

else:    
  ############################ Form generation / data capture and validation ###################


  print("Content-Type: text/html;charset=utf-8")
  print("")

  print "<html>"
  print "<head>"
  print "</head>"
  print "<title>Sensor Config</title>"
  
  print "<body>"
  print "Sensor Config<br>"
 
  configReadOK=False
  if os.path.exists("/var/www/html/config/config_script.json"):
   with open("/var/www/html/config/config_script.json",'r') as configFileRead:
     global Sensors
     Senors={}
     configReadJson = configFileRead.read()  
     configFileRead.close()
     configReadJson=json.loads(configReadJson)
     Led_Pin                  = configReadJson['Led_Pin']
     MQTT_Host                = configReadJson['MQTT_Host']
     MQTT_Port                = configReadJson['MQTT_Port']
     MQTT_User                = configReadJson['MQTT_User']
     MQTT_Pass                = configReadJson['MQTT_Pass']
     MQTT_Path_Prepend        = configReadJson['MQTT_Path_Prepend']
     SensorReader_Location    = configReadJson['SensorReader_Location']
     SensorReader_Name        = configReadJson['SensorReader_Name']
     Refresh                  = configReadJson['Refresh']
     Sensors                  = configReadJson['Sensors']
     
     configReadOK=True
  else:
     Led_Pin                  = ""
     MQTT_Host                = ""
     MQTT_Port                = ""
     MQTT_User                = ""
     MQTT_Pass                = ""
     MQTT_Path_Prepend        = ""
     SensorReader_Location    = ""
     SensorReader_Name        = ""
     Refresh                  = ""
     Sensors                  = ""

  print "<br>"

  if SensorReader_Name is None or SensorReader_Name == "":
    SensorReader_Name = socket.gethostname()
    configOK = False

  if SensorReader_Location is None:
    SensorReader_Location = ""
    configOK = False

  if MQTT_Host is None:
    MQTT_Host = ""
    configOK = False

  if MQTT_User is None:
    MQTT_User = ""

  if MQTT_Pass is None:
    MQTT_Pass = ""
    
  if MQTT_Port is None or MQTT_Port == "":
    MQTT_Port = "1883"
    configOK = False

  if MQTT_Path_Prepend is None or MQTT_Path_Prepend == "":
    MQTT_Path_Prepend = "Sensors/"
      
  if Led_Pin is None:
    Led_Pin = ""
    configOK = False

  if Refresh is None:
    Refresh = ""
    configOK = False


  print "<table style=\"width:100%\"><tr><td align=\"left\">"    
  print "<form action = \"/python/config.py\" method = \"post\">"

  print "<b>Sensor Reader Config</b><br>"
  print "*Reader Name : <input type = \"text\" name = \"SensorReader_Name\" value = \"" + SensorReader_Name +"\"> <br>"
  print "*Reader Location : <input type = \"text\" name = \"SensorReader_Location\" value = \"" + SensorReader_Location + "\"> <br>"
  print "*LED Pin : <input type = \"number\" name = \"Led_Pin\" value = \"" + Led_Pin + "\"> <br>"
  print "*Refresh Rate : <input type = \"number\" name = \"Refresh\" value = \"" + Refresh + "\" min=2 max=60> <br>"
  print "<br>"
  print "<b>MQTT Config</b><br>"
  print "*MQTT Server IP : <input type = \"text\" name = \"MQTT_Host\" value = \"" + MQTT_Host + "\"> <br>"
  print "*MQTT TCP Port : <input type = \"number\" name = \"MQTT_Port\" value = \"" + MQTT_Port + "\"> <br>"
  print "MQTT Username : <input type = \"text\" name = \"MQTT_User\" value = \"" + MQTT_User + "\"> <br>"
  print "MQTT Password : <input type = \"password\" name = \"MQTT_Pass\" value = \"" + MQTT_Pass + "\"> <br>"
  print "MQTT Topic Prepend : <input type = \"text\" name = \"MQTT_Path_Prepend\" value = \"" + MQTT_Path_Prepend + "\"> <br>"
  print "<br>"
  print "<b>Sensors Config</b><br>"
  
  if configReadOK is True:
    SensorNumber = 1
    for SensorNumber in range(1,10):
      optionLine = "Sensor Type : <select name = \"Sensors[" + str(SensorNumber) + "][Sensor_Type]\"> <option value \"\" selectedNone ></option><option value=\"DHT22\" selectedDHT22 >DHT22</option> <option value=\"1-Wire\" selected1wire >1-Wire</option> <option value=\"DryContact\" selectedDryContact >Dry Contact</option></select><br>"
      try:
        print "Sensor " + str(SensorNumber) + " Name : <input type = \"text\" name = \"Sensors[" + str(SensorNumber) + "][Sensor_Name]\" value = \"" + configReadJson['Sensors'][str(SensorNumber)]['Sensor_Name'] + "\"> <br>"
        print "Sensor " + str(SensorNumber) + " Location : <input type = \"text\" name = \"Sensors[" + str(SensorNumber) + "][Sensor_Location]\" value = \"" + configReadJson['Sensors'][str(SensorNumber)]['Sensor_Location'] + "\"> <br>"
        print "Sensor " + str(SensorNumber) + " Address : <input type = \"text\" name = \"Sensors[" + str(SensorNumber) + "][Sensor_Address]\" value = \"" + configReadJson['Sensors'][str(SensorNumber)]['Sensor_Address'] + "\"> <i>GPIO Pin or 1-Wire bus address</i><br>"
        print "Sensor " + str(SensorNumber) + " Refresh : <input type = \"text\" name = \"Sensors[" + str(SensorNumber) + "][Sensor_Refresh]\" value = \"\"> <br>"
            
        if configReadJson['Sensors'][str(SensorNumber)]['Sensor_Type'] == "DHT22":
          optionLine = optionLine.replace("selectedNone", "", 1)
          optionLine = optionLine.replace("selectedDHT22", "selected", 1)
          optionLine = optionLine.replace("selected1wire", "", 1)
          optionLine = optionLine.replace('selectedDryContact', '',1)
        elif configReadJson['Sensors'][str(SensorNumber)]['Sensor_Type'] == "1-Wire":
          optionLine = optionLine.replace('selectedNone', '',1)
          optionLine = optionLine.replace('selectedDHT22', '',1)
          optionLine = optionLine.replace('selected1wire', 'selected',1)
          optionLine = optionLine.replace('selectedDryContact', '',1)
        elif configReadJson['Sensors'][str(SensorNumber)]['Sensor_Type'] == "DryContact":
          optionLine = optionLine.replace('selectedNone', '',1)
          optionLine = optionLine.replace('selectedDHT22', '',1)
          optionLine = optionLine.replace('selected1wire', '',1)
          optionLine = optionLine.replace('selectedDryContact', 'selected',1)
        else:
          optionLine = optionLine.replace('selectedNone', 'selected',1)
          optionLine = optionLine.replace('selectedDHT22', '',1)
          optionLine = optionLine.replace('selected1wire', '',1)
          optionLine = optionLine.replace('selectedDryContact', '',1)
          
        print optionLine
        print "<br>"
      except KeyError:
        print "Sensor " + str(SensorNumber) + " Name : <input type = \"text\" name = \"Sensors[" + str(SensorNumber) + "][Sensor_Name]\" value = \"\"> <br>"
        print "Sensor " + str(SensorNumber) + " Location : <input type = \"text\" name = \"Sensors[" + str(SensorNumber) + "][Sensor_Location]\" value = \"\"> <br>"
        print "Sensor " + str(SensorNumber) + " Address : <input type = \"text\" name = \"Sensors[" + str(SensorNumber) + "][Sensor_Address]\" value = \"\"> <i>GPIO Pin or 1-Wire bus address</i><br>"
        print optionLine
        print "<br>" 
  else:
    SensorNumber = 1
    for SensorNumber in range(1,8):  
      print "Sensor " + str(SensorNumber) + " Name : <input type = \"text\" name = \"Sensors[" + str(SensorNumber) + "][Sensor_Name]\" value = \"\"> <br>"
      print "Sensor " + str(SensorNumber) + " Location : <input type = \"text\" name = \"Sensors[" + str(SensorNumber) + "][Sensor_Location]\" value = \"\"> <br>"
      print "Sensor " + str(SensorNumber) + " Address : <input type = \"text\" name = \"Sensors[" + str(SensorNumber) + "][Sensor_Address]\" value = \"\"> <i>GPIO Pin or 1-Wire bus address</i><br>"
      print "Sensor " + str(SensorNumber) + " Refresh : <input type = \"text\" name = \"Sensors[" + str(SensorNumber) + "][Sensor_Refresh]\" value = \"\">  <i> Not Mandatory, if blank, will default to the general refresh</i><br>"

      print "Sensor Type : <select name = \"Sensors[" + str(SensorNumber) + "][Sensor_Type]\"> <option value \"\" selectedNone ></option><option value=\"DHT22\" selectedDHT22 >DHT22</option> <option value=\"1-Wire\" selected1wire >1-Wire</option></select> <br>"
      print "<br>"        
    
  print "<input type = \"hidden\" name = \"NewConfig\" value = \"True\"> <br>"
  print "<input type = \"submit\" value = \"Apply Config\" />"
    
  print "</form>"
  print "</td><td align=\"left\">"
  print "<b>    Raspberry PI 2/3 Pin Out mapping</b></br>"
  print "<img src=\"/images/RaspberryPI_Pinout.png\">"
  print "<br>"
  print "<b>1-Wire devices found</b><br>"
  # /sys/bus/w1/devices
  OneWireProbes = ""
  OneWireProbes = listdir("/sys/bus/w1/devices")
  OneWireProbeCount=0
  while OneWireProbeCount < len(OneWireProbes):
     if "28" in OneWireProbes[OneWireProbeCount]: 
       print OneWireProbes[OneWireProbeCount] + "<br>"   
     OneWireProbeCount += 1
  print "</td>"
  print "</tr></table>"
  print "<table>"
  print "<tr><td>"
  print "<form method=\"post\" action=\"/index.html\"><button type=\"submit\">OK</button></form>"
  print "</td>"
  print "<td>"
  print "<form method=\"post\" action=\"/index.html\"><button type=\"submit\">Cancel</button></form>"
  print "</tr></td>"
  print "</table>"
  print "</body>"
  print "</html>"
