"""
Organization: Professorship of Environmental Sensing and Modelling, TU Munich
Date: 08.03.2022
Author: Daniel Kühbacher

Description: This class can be used to read out EC gas modules.
"""

import serial
from time import sleep

class ec_sensor:
    
    types = {'0x21': 'NO2', '0x23': 'O3', '0x19': 'CO'}
    units = {'0x2': 'ppm', '0x4': 'ppb', '0x8': '%'}

    def __init__(self, port):
        """
            ### Constructor ###
            Establishes connection to sensor and checks the sensor type, unit and measurment range
        """
        
        try:
            # connect to sensor
            self.ser = serial.Serial(port,
                                baudrate = 9600,
                                parity = serial.PARITY_NONE,
                                stopbits = serial.STOPBITS_ONE,
                                bytesize = serial.EIGHTBITS,
                                timeout = 1)
            
            # get sensor information
            self.ser.write(b'\xD1')
            info_bin = list(self.ser.read(8))

            self.sensor_type = self.types[hex(info_bin[0])] 
            self.unit = self.units[hex(info_bin[3])]
            self.max_value = (info_bin[1] << 8)+ info_bin[2]
            self.decimal = info_bin[7]>>4
            
            #flush buffer
            self.ser.flush()
            
        except serial.SerialException:
            print('Cannot connect to the device')
        
   
    def read_sensor(self, delay = 0.01):
        """
            Description: Sensor single readout of gas concentration, temperature and humidity
            Paramerters: delay - determines delay between write and read command. default = 0.01s
            Return: list of floats contining the sensor values in the following order: gas, temperature, humidity
        """
        
        # Gas concentration, temperature and humidity readout
        self.ser.write(b'\xFF\x00\x87\x00\x00\x00\x00\x00\x79')
        
        # Sleep for defined time before reading the sensor
        sleep(delay)
        
        #read sensor value
        value = self.ser.read(13)
        
        # convert gas concentration
        self.gas = (float)(value[7] << 8)+ value[8]
        self.gas = self.gas/pow(10,self.decimal)
        
        #convert temperature
        self.temperature = (float)(value[9] << 8)+ value[10]
        self.temperature = self.temperature/100
        
        #convert humidity
        self.humidity = (float)(value[11] << 8)+ value[12]
        self.humidity = self.humidity/100
        
        #flush buffer
        self.ser.flush()
        
        return [self.gas, self.temperature, self.humidity]
        
        
    def bulk_readout(self, delay, iterations):
        """
            Description: Multiple sensor readout -> returns average value 
            Paramerters: delay - determines delay between each iteration
                         iterations - determines number of iterations
            Return: list of averaged sensor values in the following order: gas, temperature, humidity
        """
        
        concentration = 0
        humidity = 0
        temperature = 0
        
        for i in range(0,iterations):
            
            # read out sensor value
            dat = self.read_sensor(delay= 0.01)
             
            # add measured value 
            concentration = concentration + dat[0]
            temperature = temperature + dat[1]
            humidity = humidity + dat[2]
            
            # sleep for defined time
            sleep(delay)
        
        # divide values by number of iterations
        concentration = concentration/iterations
        humidity = humidity/iterations
        temperature = temperature/iterations
        
        
        return [concentration, temperature, humidity]
    
    def led_status(self,status_true):
        if status_true:
            #write LED off
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
    port = '/dev/ttyAMA2'
    ec = ec_sensor(port)
    
    print('{} Sensor at port {}'.format(ec.sensor_type, port))
    print("Maximal value: {}{}".format(ec.max_value, ec.unit))
    
    dat = ec.bulk_readout(0.1, 10)
    
    print('\nMeasured values:')
    print('Gas concentration: {0:.4f}'.format(dat[0])+ec.unit)
    print('Temperature: {0:.1f} °C'.format(dat[1]))
    print('Humidity: {0:.1f} %rH'.format(dat[2]))
    
    ec.led_status(False)
    
    del ec