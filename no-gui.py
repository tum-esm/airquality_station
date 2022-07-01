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
from stv_client import STVClient


class MeasureAirquality:

    def __init__(self, sensor_id):
        """
            Description: Constructor
            Parameters: db_path: path to sqlite3 database
        """
        self._sensor_id = sensor_id

        #set GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(27,GPIO.OUT)

        # TODO: Possibly swap connections
        # init sensors and serial ports
        self.ec_o3 = EcSensor('/dev/ttyAMA1') #O3 Sensor
        self.ec_co = EcSensor('/dev/ttyAMA2') #CO Sensor
        self.ec_no2 = EcSensor('/dev/ttyS0') #NO2 Sensor

        # Client für Stickoxide
        self.client = STVClient(
            database_name="stv_airquality_course",
            table_name="sensor_node",
            data_columns=["no2"],
            units={"no2": "µg/m³"},
            descriptions={"no2": "Sensorwert Stickoxide"},
            minima={"no2": 0},
            decimal_places={"no2": 1},
            print_stuff=False,
        )
        # Client für alle Sensorwerte
        self.client_verbose = STVClient(
            database_name="stv_airquality_course",
            table_name="sensor_node_verbose",
            data_columns=["no2", "co", "o3", "temperatur", "luftfeuchtigkeit"],
            units={"no2": "µg/m³", "co": "mg/m³","o3": "µg/m³", "temperatur": "°C", "luftfeuchtigkeit": "%rH"},
            descriptions={"no2": "Stickstoffdioxid", "co": "Kohlenmonoxid", "o3": "Ozon"},
            minima={"no2": 0, "co": 0, "o3": 0, "luftfeuchtigkeit": 0},
            decimal_places={"no2": 1, "co": 2, "o3": 1, "temperatur": 1, "luftfeuchtigkeit": 1},
            print_stuff=False,
        )
        
        print('Connected to airquality database')


    def measurement_cycle(self, vent_time=5, wait_time=2, iterations=5) -> dict:
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
        
        conv_o3 = 1.96
        conv_co = 1.15
        conv_no2 = 1.88

        values = {  self.ec_o3.sensor_type:(con_o3*conv_o3), # convert o3 values from ppb to µg/m³
                    self.ec_no2.sensor_type:(con_no2*1000)*conv_no2, # convert no2 values from ppm to µg/m³
                    self.ec_co.sensor_type:(con_co)*conv_co, # convert co values from ppm to mg/m³
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

                var = self.measurement_cycle(vent_time=5, wait_time=2, iterations=5)
                self.client.insert_data(self._sensor_id, {"no2": var["NO2"]})
                self.client_verbose.insert_data(self._sensor_id,
                                                {"no2" : var["NO2"], "co" : var["CO"], "o3" : var["O3"],
                                                 "temperatur" : var["temperature"],
                                                 "luftfeuchtigkeit" : var["humidity"]})
           
                # make logging message
                logging.info("New Measurement")
                print("---")
                print("|      NO2    : {0:.2f} µg/m³".format(var['NO2']))
                print("|      O3     : {0:.2f} µg/m³".format(var['O3']))
                print("|      CO     : {0:.2f} mg/m³".format(var['CO']))
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
        del self.client
        del self.client_verbose
        GPIO.cleanup()


if __name__ == "__main__":

    print('Air quality measurement station v1.1 (no GUI)')
    print('Press Ctrl+C to close the program...')

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    ### Start of the measurements
    print('\n\nStart logging...')

    # TODO: Adjust node name
    measurement_obj = MeasureAirquality(sensor_id = "node 1")
    measurement_obj.measure(time_between_cycles = 15)

    del measurement_obj
    #### End of Measurements
    print("Program end") 