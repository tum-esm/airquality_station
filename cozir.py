"""
Organization: Professorship of Environmental Sensing and Modelling, TU Munich
Date: 08.03.2022
Author: Daniel Kuehbacher

Description: This class can be used to read ec sensors via UART on a Raspberry pi.
"""

import serial
from time import sleep

class CozirSensor:

    def __init__(self, port):
        """
            ### Constructor ###
            Establishes connection to sensor and checks the sensor type, unit and measurement range
            Initializes variables
        """

        for i in range(0,10): # perform 10 retries if it does not connect
            try:
                # connect to sensor
                self.ser = serial.Serial(port,
                                    baudrate = 9600,
                                    parity = serial.PARITY_NONE,
                                    stopbits = serial.STOPBITS_ONE,
                                    bytesize = serial.EIGHTBITS,
                                    timeout = 1)
                sleep(0.1) # sleep before continue

                self.sensor_type = 'CO2'
                self.unit = 'ppm'
                self.max_value = 5000
                self.eol = b'\r\n'

                #flush buffer
                self.ser.flush()
                break

            except:
                print('Cannot connect to port {}. Attempt {}'.format(port,i))
                sleep(0.5)
                
    
    def read(self):
        """
            Description: Sensor single readout of gas concentration, temperature and humidity
            Parameters: delay - determines delay between write and read command. default = 0.01s
            Return: list of floats containing the sensor values in the following order: gas, temperature, humidity
        """
        # Get measurment
        self.ser.read_until(self.eol)
        sensor_reading = self.ser.read_until(self.eol)
        concentration_filtered = int(sensor_reading[3:8])
        concentration_unfiltered = int(sensor_reading[11:16])
        
        sleep(0.1)
        #flush buffer
        self.ser.flush()
        
        return [concentration_filtered, concentration_unfiltered]


    def read_bulk(self, delay, iterations):
        """
            Description: Multiple sensor readout -> returns average value 
            Parameters: delay - determines delay between each iteration
                         iterations - determines number of iterations
            Return: list of averaged sensor values in the following order: gas, temperature, humidity
        """
        
        concentration_filtered = 0
        concentration_unfiltered = 0
        
        for _ in range(0,iterations):
            
            # read out sensor value
            var = self.read()
             
            # add measured value 
            concentration_filtered += var[0]
            concentration_unfiltered += var[1]
            
            # sleep for defined time
            sleep(delay)
        
        # divide values by number of iterations
        concentration_filtered = concentration_filtered/iterations
        concentration_unfiltered = concentration_unfiltered/iterations
        
        return [concentration_filtered, concentration_unfiltered]
    
        
    def __del__(self):
        """
            ### Destructor ###
        """
        self.ser.flush()
        self.ser.close()
        
        
# test class
if __name__ == "__main__":

    # test on port
    port = '/dev/ttyAMA3'
    sensor = CozirSensor(port)
    
    print('{} Sensor at port {}'.format(sensor.sensor_type, port))
    print("Maximal value: {}{}".format(sensor.max_value, sensor.unit))
    
    dat = sensor.read_bulk(0.1, 10)
    
    print('\nMeasured values:')
    print('Gas concentration: {0:.4f}'.format(dat[0])+sensor.unit)

    del sensor