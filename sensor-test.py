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

    # test ventilator
    # TODO: Test the ventilator. Turn GPIO 27 on and off
    # Use GPIO.output() for this
    # 3 lines

    # TODO: Now it is time to connect the UART Sensors
    # Connect with the following ports: '/dev/ttyS0', '/dev/ttyAMA1', '/dev/ttyAMA2'
    # read out the sensor specifications (type, units etc...), the concentration and the temperature/humidity.
    # print the values in the console.
    # 5-10 lines

    print("\n\n<<< Test finished... >>>")