#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import os
import os.path
from os import path
import socket
import syslog
import sys
import psutil

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




def PrintThis (StringToPrint):
   global printToConsole
   if printToConsole:
      print str(datetime.datetime.now()) + " - " + str(StringToPrint)
   else:
      syslog.syslog(str(StringToPrint))

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

GPIO.setmode(GPIO.BCM)
# 16 = Small Button
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# 20 = Vibration Sensor
GPIO.setup(20, GPIO.IN)
# 21 = Large Button
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
lowBatteryState = False
fireDetectedState = False
VibrationState = False
while True:
    input_stateGPIO21 = GPIO.input(21)
    input_stateGPIO16 = GPIO.input(16)
    input_stateGPIO20 = GPIO.input(20)
    # 21 = large button
    if input_stateGPIO21 == False and input_stateGPIO16 == False:
       PrintThis("both button pressed initiating shutdown")
       PrintThis(os.system("shutdown"))
       open('/tmp/Shutdown', "a").close()
       break
    if input_stateGPIO21 == False:
        if lowBatteryState == True:
          lowBatteryState = False
          PrintThis('Low Battery off')
	  os.remove("/tmp/LowBattery")
	else:
 	  open('/tmp/LowBattery', "a").close()
          lowBatteryState = True
          PrintTHis('Low Battery on')
    # 16 = large button
    if input_stateGPIO16 == False:
        if fireDetectedState == True:
          fireDetectedState = False
          PrintThis('Fire Detected off')
	  os.remove("/tmp/FireDetected")
	else:
 	  open('/tmp/FireDetected', "a").close()
          fireDetectedState = True
          PrintThis('Fire Detected on')
    # 20 = vibration sensor
    if input_stateGPIO20 == True:
       open('/tmp/VibrationDetected', "a").close()
       PrintThis('Vibration Detected')
    else:
        if path.exists('/tmp/VibrationDetected'):
            now = time.time()
            fileTime = os.path.getmtime('/tmp/VibrationDetected')
            if now > fileTime + 60:
                PrintThis("file is older than 60 sec deleting")
                os.remove("/tmp/VibrationDetected")
    time.sleep(0.2)
