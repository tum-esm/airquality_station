"""
Organization: Professorship of Environmental Sensing and Modelling, TU Munich
Date: 08.03.2022
Author: Daniel Kuehbacher

Description: This class can be used to read ec sensors via UART on a Raspberry pi.
"""

import serial
from time import sleep

class EcSensor:
    # sensor types used in the project can be read out
    types = {'0x21': 'NO2', '0x23': 'O3', '0x19': 'CO'}
    units = {'0x2': 'ppm', '0x4': 'ppb', '0x8': '%'}

    def __init__(self, port):
        """
            ### Constructor ###
            Establishes connection to sensor and checks the sensor type, unit and measurement range
            Initializes variables
        """

        for i in range(0,10): # perform 10 retries if it does not connect
            try:
                # connect to sensor
                # TODO -> Check the datasheet and update he serial settings
                self.ser = serial.Serial(#ADD SETTINGS HERE)

                sleep(0.1) # sleep before continue

                # get sensor information
                self.ser.write(b'\xD1')
                sleep(0.1)
                info_bin = list(self.ser.read(8))

                self.sensor_type = self.types[hex(info_bin[0])]
                self.unit = self.units[hex(info_bin[3])]
                self.max_value = (info_bin[1] << 8)+ info_bin[2]
                self.decimal = info_bin[7]>>4

                #flush buffer
                self.ser.flush()
                break

            except:
                print('Cannot connect to the device. Attempt {}'.format(i))
                sleep(0.5)


    def read(self, delay = 0.1):
        """
            Description: Sensor single readout of gas concentration, temperature and humidity
            Parameters: delay - determines delay between write and read command. default = 0.01s
            Return: list of floats containing the sensor values in the following order: gas, temperature, humidity
        """
        
        # TODO: Check the datasheet and add the read command below. 
        # Gas concentration, temperature and humidity readout -> Check datasheet for information
        self.ser.write(#ADD READ COMMAND HERE)

        # Sleep for defined time before reading the sensor
        sleep(delay)

        # read sensor value
        readout = self.ser.read(13)
        
        # convert gas concentration
        gas_concentration =  ((readout[7] << 8) + readout[8]) / pow(10, self.decimal)
        # convert temperature
        temperature = ((readout[9] << 8)+ readout[10]) / 100
        # convert humidity
        humidity = ((readout[11] << 8)+ readout[12]) / 100

        #flush buffer
        self.ser.flush()
        
        return [gas_concentration, temperature, humidity]


    def read_bulk(self, delay, iterations):
        """
            Description: Multiple sensor readout -> returns average value 
            Parameters: delay - determines delay between each iteration
                         iterations - determines number of iterations
            Return: list of averaged sensor values in the following order: gas, temperature, humidity
        """
        
        concentration = 0
        humidity = 0
        temperature = 0
        
        for i in range(0,iterations):
            
            # read out sensor value
            var = self.read()
             
            # add measured value 
            concentration += var[0]
            temperature += var[1]
            humidity += var[2]
            
            # sleep for defined time
            sleep(delay)
        
        # divide values by number of iterations
        concentration = concentration/iterations
        humidity = humidity/iterations
        temperature = temperature/iterations

        return [concentration, temperature, humidity]


    def change_led_status(self, status):
        if status:
            #write LED on
            self.ser.write(b'\xFF\x01\x89\x00\x00\x00\x00\x00\x76')
        else:
            #write LED off
            self.ser.write(b'\xFF\x01\x88\x00\x00\x00\x00\x00\x77')

        #flush buffer
        self.ser.flush()
        
        
    def __del__(self):
        """
            ### Destructor ###
        """
        self.ser.flush()
        self.ser.close()
        
        
# test class
if __name__ == "__main__":

    # test on port
    port = '/dev/ttyS0'
    sensor = EcSensor(port)
    
    print('{} Sensor at port {}'.format(sensor.sensor_type, port))
    print("Maximal value: {}{}".format(sensor.max_value, sensor.unit))
    
    dat = sensor.read_bulk(0.1, 10)
    
    print('\nMeasured values:')
    print('Gas concentration: {0:.4f}'.format(dat[0])+sensor.unit)
    print('Temperature: {0:.1f} °C'.format(dat[1]))
    print('Humidity: {0:.1f} %rH'.format(dat[2]))
    
    #sensor.led_status(change_led_status)

    del sensor