"""
Can be used to test the sensor and the ventilator
"""
import RPi.GPIO as GPIO
import time
import serial

# init ventilator GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(27,GPIO.OUT)

types = {'0x21': 'NO2', '0x23': 'O3', '0x19': 'CO'}
units = {'0x2': 'ppm', '0x4': 'ppb', '0x8': '%'}

def sensor_test(port):
    
    # connect to sensor
    ser = serial.Serial(port,
                        baudrate = 9600,
                        parity = serial.PARITY_NONE,
                        stopbits = serial.STOPBITS_ONE,
                        bytesize = serial.EIGHTBITS,
                        timeout = 1)
    
    # get sensor information
    ser.write(b'\xD1')
    info_bin = list(ser.read(8))

    decimal = info_bin[7]>>4
    unit = units[hex(info_bin[3])]
    
    print('\n\n  {} Sensor at port {}'.format(types[hex(info_bin[0])], port))
    print("  Maximal value: {}{}".format((info_bin[1] << 8)+ info_bin[2], unit))
    
    # Gas concentration, temperature and humidity readout
    ser.write(b'\xFF\x00\x87\x00\x00\x00\x00\x00\x79')
    
    # Sleep for defined time before reading the sensor
    time.sleep(0.01)
    #read sensor value
    value = ser.read(13)
    
    # convert gas concentration
    gas = (float)(value[7] << 8)+ value[8]
    gas = gas/pow(10,decimal)
    
    #convert temperature
    temperature = (float)(value[9] << 8)+ value[10]
    temperature = temperature/100
    
    #convert humidity
    humidity = (float)(value[11] << 8)+ value[12]
    humidity = humidity/100
    
    
    print('|>------------------------------')
    print('|> Gas concentration: {0:.4f}'.format(gas)+unit)
    print('|> Temperature: {0:.1f} °C'.format(temperature))
    print('|> Humidity: {0:.1f} %rH'.format(humidity))
    print('|>------------------------------')
    
    ser.write(b'\xFF\x01\x88\x00\x00\x00\x00\x00\x77')
    
    ser.flush()
    ser.close()

if __name__ == "__main__":
    print("<<< Test sensor assembly. >>>")
    print("Ventilator test...")
    
    # test ventilator
    GPIO.output(27,True)
    time.sleep(1)
    GPIO.output(27,False)


    print("Sensor test...")
    
    sensor_test('/dev/ttyS0')
    sensor_test('/dev/ttyAMA1')
    sensor_test('/dev/ttyAMA2')
    
    print("\n\n<<< Test finished... >>>")