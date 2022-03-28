"""
The sensor unit has a controllable ventilator that should suck in air for measurements.
This script can be used to test the ventilator.
Please make sure, the ventilator is connected to Pin 3 on the Raspberry Pi. 
"""

import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(3,GPIO.OUT)

for i in range(0,5):
    GPIO.output(3,True)
    time.sleep(4)
    GPIO.output(3,False)
    time.sleep(3)
    
print("Test finished...")
print("Test succeeded if ventilator was activated 5 times.")
