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
                # TODO -> Check the datasheet and set the right baudrate in the
                # function below.
                # For more information about the library
                # check https://pyserial.readthedocs.io/en/latest/pyserial.html
                self.ser = serial.Serial(port, baudrate = 0,
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
                print(f'Cannot connect to the device. Attempt {i}')#.format(i))
                print("Error: " + str(error_message))
                sleep(0.5)


    def read(self, delay = 0.1):
        """
            Description: Sensor single readout of gas concentration, temperature and humidity
            Parameters: delay - determines delay between write and read command. default = 0.01s
            Return: list of floats containing the sensor values in the following order: gas,
                    temperature, humidity
        """

        # TODO: Check the datasheet and add update the command below
        # The command is the same for all sensors -> Hint: check Command 6
        self.ser.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00')

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

    dat = sensor.read()

    print('\nMeasured values:')
    print(f'Gas concentration: {dat[0]:.4f}{sensor.unit}')
    print(f'Temperature: {dat[1]:.1f} °C')
    print(f'Humidity: {dat[2]:.1f} %rH')

    del sensor
    