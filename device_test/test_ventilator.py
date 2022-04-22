"""
The sensor unit has a controllable ventilator that should suck in air for measurements.
This script can be used to test the ventilator.
Please make sure, the ventilator is connected to Pin 3 on the Raspberry Pi. 
"""

import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(27,GPIO.OUT)

for i in range(0,5):
    GPIO.output(27,True)
    time.sleep(2)
    GPIO.output(27,False)
    time.sleep(1)
    
print("Test finished...")
print("Test succeeded if ventilator was activated 5 times.")
