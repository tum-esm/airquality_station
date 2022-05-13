"""
Can be used to test the sensor and the ventilator
"""
import RPi.GPIO as GPIO
from ecsense import EcSensor
import time

# init ventilator GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)

if __name__ == "__main__":

    print("<<< Test sensor assembly. >>>")

    # Ventilator test
    # Activate the ventilator by turning GPIO 27 on and off 
    # Use the function GPIO.output().
    # More information at: https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
    
    # TODO: turn GPIO on 
    time.sleep(3) # sleep for 3 seconds
    # TODO: turn GPIO off
    
    # Sensor test
    # Connect to all sensors using the EcSensor class and read their properties and values. 
    # Check ecsense.py (main function) how to instantiate and read the sensors. 
    # The sensors are connected to the following ports: '/dev/ttyS0', '/dev/ttyAMA1', '/dev/ttyAMA2'

    # TODO: Connect to sensor 1 on the first port
    # TODO: Read the sensor properties and the measurement value and print it in the console.
    # TODO: Repead the two steps above for sensor 2 and sensor 3 

    print("\n\n<<< Test finished... >>>")