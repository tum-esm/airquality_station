"""
Organization: Professorship of Environmental Sensing and Modelling, TU Munich
Date: 14.04.2022
Author: Daniel Kühbacher

Description: This script reads our sensors and saves the measured values in a
sqlite database.
"""

from socket import timeout
import RPi.GPIO as GPIO
import time
import logging
import sqlite3

from datetime import datetime
from ecsense import EcSensor
from stv_client.client import STVClient


class MeasureAirquality:

    def __init__(self, sensor_id):
        """
            Description: Constructor
            Parameters: db_path: path to sqlite3 database
        """

        #set GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(27,GPIO.OUT)

        #init sensors and serial ports
        self.ec_o3 = EcSensor('/dev/ttyS0') #O3 Sensor
        self.ec_co = EcSensor('/dev/ttyAMA1') #CO Sensor
        self.ec_no2 = EcSensor('/dev/ttyAMA2') #NO2 Sensor

        # connect to database
        self.client = STVClient(
            database_name = "airquality_course",
            table_name = "device_data",
            data_columns=["concentration", "temperature", "humidity"],
        )
        print('Connected to airquality database')


    def measurement_cycle(self, vent_time=2, wait_time=2, iterations=5) -> dict:
        """
            Description: ventilates measurement channel and reads out sensors
            Parameters: vent_time: ventilation time
                        wait_time: wait time after ventilation
                        iterations: number of measurements that are averaged 
            Return: dict which holds the measured gas concentration, temperature and humidity
        """

        # ventilate channel 
        GPIO.output(27,True)
        time.sleep(vent_time)
        GPIO.output(27,False)
        time.sleep(wait_time)

        [con_o3, temp_o3, hum_o3] = self.ec_o3.read_bulk(iterations=iterations, delay=0.2)
        [con_co, temp_co, hum_co] = self.ec_co.read_bulk(iterations=iterations, delay=0.2)
        [con_no2, temp_no2, hum_no2] = self.ec_no2.read_bulk(iterations=iterations, delay=0.2)

        values = {  self.ec_o3.sensor_type:(con_o3/1000), # convert o3 values to ppm
                    self.ec_no2.sensor_type:con_no2,
                    self.ec_co.sensor_type:con_co,
                    'temperature':(temp_o3 + temp_co + temp_no2)/3,
                    'humidity':(hum_o3+ hum_no2+ hum_co)/3}

        return values


    def measure(self, time_between_cycles = 30):
        """
            Description: measure gas concentration in a loop and save measured values in database
        """
        logging.info("Main    : Starting measurements")

        loop_forever=True
        while loop_forever:
            try:
                execution_started_at = datetime.now().timestamp()

                var = self.measurement_cycle(vent_time=15, wait_time=2, iterations=5)

                for gas in ["NO2", "O3", "CO"]:
                    self.client.insert_data(
                        f"{self.sensor_id}_{gas}",
                        {
                            "concentration": var[gas],
                            "temperature": var["temperature"],
                            "humidity":var["humidity"]
                        }
                    )

                self.con.commit()  # safe data in database

                # make logging message
                logging.info("New Measurement")
                print("---")
                print("|      NO2    : {0:.4f} ppm".format(var['NO2']))
                print("|      O3     : {0:.4f} ppm".format(var['O3']))
                print("|      CO     : {0:.4f} ppm".format(var['CO']))
                print("| Temperature : {0:.1f} °C".format(var['temperature']))
                print("|   Humidity  : {0:.1f} rH".format(var['humidity']))
                print("---\n")

                execution_ended_at = datetime.now().timestamp()
                time_to_wait = time_between_cycles - (execution_ended_at - execution_started_at)
                time_to_wait = 0 if time_to_wait < 0 else time_to_wait
                time.sleep(time_to_wait)

            except KeyboardInterrupt:
                loop_forever = False

    def __del__(self):
        """
            Description: Destructor; close db connection and cleanup GPIOs
        """
        del self.client()
        GPIO.cleanup()


if __name__ == "__main__":

    print('Air quality measurement station v1.1 (no GUI)')
    print('Press Ctrl+C to close the program...')

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    ### Start of the measurements
    print('\n\nStart logging...')

    measurement_obj = MeasureAirquality(sensor_id = "station_1")
    measurement_obj.measure(time_between_cycles = 45)

    del measurement_obj
    #### End of Measurements
    print("Program end") 