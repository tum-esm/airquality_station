"""
Can be used to test the sensor and the ventilator
"""
from time import sleep
from cozir import CozirSensor

if __name__ == "__main__":
    print("<<< Test sensor. >>>")
    
    co2_sensor = CozirSensor('/dev/ttyAMA3')
    sleep(0.1) # sleep before continue# get sensor information
    
    # Get measurment 
    sensor_reading = co2_sensor.read()
    # sensor_reading = co2_sensor.read_bulk(delay=0.1, iterations=10)
    
    # Print measurements
    print("CO2 filtered = {} ppm | CO2 unfiltered = {} ppm".format(int(sensor_reading[0]),
                                                                   int(sensor_reading[1])))
    
    print("\n\n<<< Test finished... >>>")