"""
Can be used to test the sensor and the ventilator
"""
import RPi.GPIO as GPIO
import ecsense

# init ventilator GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)

if __name__ == "__main__":
    print("<<< Test sensor assembly. >>>")
    print("Ventilator test...")

    # test ventilator
    GPIO.output(27, True)
    time.sleep(1)
    GPIO.output(27, False)

    print("Sensor test...")

    sensors = [EcSensor('/dev/ttyS0'), EcSensor('/dev/ttyAMA1'), EcSensor('/dev/ttyAMA2')]

    for sensor in sensors:
        [gas_concentration, temperature, humidity] = sensor.read()

        print('|>------------------------------')
        print('|> Gas concentration: {0:.4f}'.format(gas_concentration) + sensor.unit)
        print('|> Temperature: {0:.1f} °C'.format(temperature))
        print('|> Humidity: {0:.1f} %rH'.format(humidity))
        print('|>------------------------------')

    print("\n\n<<< Test finished... >>>")