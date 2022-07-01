"""
Organization: Professorship of Environmental Sensing and Modelling, TU Munich
Date: 08.03.2022
Author: Daniel Kuehbacher

Description: This class can be used to read ec sensors via UART on a Raspberry pi.
"""

from time import sleep
import serial


class EcSensor:
    """
    Class for EC-Sensor connection usage.
    """
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
                self.ser = serial.Serial(port, baudrate = 9600,
                                    parity = serial.PARITY_NONE,
                                    stopbits = serial.STOPBITS_ONE,
                                    bytesize = serial.EIGHTBITS,
                                    timeout = 1)

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

            except Exception as error_message:
                print(f'Cannot connect to the device. Attempt {i}')
                print("Error: " + str(error_message))
                sleep(0.5)


    def read(self, delay = 0.1):
        """
            Description: Sensor single readout of gas concentration, temperature and humidity
            Parameters: delay - determines delay between write and read command. default = 0.01s
            Return: list of floats containing the sensor values in the following order: gas,
                    temperature, humidity
        """
        self.ser.write(b'\xff\x01\x87\x00\x00\x00\x00\x00\x78')
        sleep(delay)
        readout = self.ser.read(13)

        gas_concentration =  ((readout[7] << 8) + readout[8]) / pow(10, self.decimal)
        temperature = ((readout[9] << 8)+ readout[10]) / 100
        humidity = ((readout[11] << 8)+ readout[12]) / 100

        self.ser.flush() #flush serial buffer
        return [gas_concentration, temperature, humidity]


    def read_bulk(self, delay, iterations):
        """
            Description: Multiple sensor readout -> returns average value
            Parameters: delay - determines delay between each iteration
                         iterations - determines number of iterations
            Return: list of averaged sensor values in the following order: gas,
                    temperature, humidity
        """

        concentration = 0
        humidity = 0
        temperature = 0

        for i in range(0,iterations):
            var = self.read() # read out sensor value
            concentration += var[0]
            temperature += var[1]
            humidity += var[2]
            sleep(delay)

        # divide values by number of iterations
        concentration = concentration/iterations
        humidity = humidity/iterations
        temperature = temperature/iterations
        return [concentration, temperature, humidity]


    def change_led_status(self, status):
        """
        Change sensor led blinking status.
        """
        if status:
            self.ser.write(b'\xFF\x01\x89\x00\x00\x00\x00\x00\x76') #LED on
        else:
            self.ser.write(b'\xFF\x01\x88\x00\x00\x00\x00\x00\x77') #LED off
        self.ser.flush()


    def __del__(self):
        """
            ### Destructor ###
        """
        self.ser.flush()
        self.ser.close()


# test class
if __name__ == "__main__":

    # test on defined port
    PORT = '/dev/ttyS0'
    sensor = EcSensor(PORT)

    print(f'{sensor.sensor_type} Sensor at port {PORT}')
    print(f'Maximal value: {sensor.max_value}{sensor.unit}')

    dat = sensor.read_bulk(0.1, 10)

    print('\nMeasured values:')
    print(f'Gas concentration: {dat[0]:.4f}{sensor.unit}')
    print(f'Temperature: {dat[1]:.1f} °C')
    print(f'Humidity: {dat[2]:.1f} %rH')

    del sensor
    