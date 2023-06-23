"""
Organization: Professorship of Environmental Sensing and Modelling, TU Munich
Date: 14.04.2022
Author: Daniel Kühbacher

Description: This script reads our sensors and saves the measured values in a
sqlite database.
"""

import time
import logging
import RPi.GPIO as GPIO
import os
import dotenv
from datetime import datetime

from ecsense import EcSensor
from cozir import CozirSensor

from tum_esm_signal import TUM_ESM_SignalClient


class MeasureAirquality:
    """
    Air-quality measurement class.pip 
    """

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
        self.ec_o3 = EcSensor('/dev/ttyS0') #O3 Sensor
        self.ec_co = EcSensor('/dev/ttyAMA1') #CO Sensor
        self.ec_no2 = EcSensor('/dev/ttyAMA2') #NO2 Sensor
        self.cozir_co2 = CozirSensor('/dev/ttyAMA3') #CO2 Sensor
        
        # intialize bias values
        self.CO2_BIAS = -750
        self.NO2_BIAS = 0
        self.CO_BIAS = 0
        self.O3_BIAS = 0


        dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

        SIGNAL_CLIENT_IDENTITY = os.getenv("TUM_ESM_SIGNAL_CMS_IDENTITY")
        assert (
            SIGNAL_CLIENT_IDENTITY is not None
        ), "TUM_ESM_SIGNAL_CMS_IDENTITY environment variable not set"

        SIGNAL_CLIENT_PASSWORD = os.getenv("TUM_ESM_SIGNAL_CMS_PASSWORD")
        assert (
            SIGNAL_CLIENT_PASSWORD is not None
        ), "TUM_ESM_SIGNAL_CMS_PASSWORD environment variable not set"
        

        signal_client = TUM_ESM_SignalClient(
            cms_identity = SIGNAL_CLIENT_IDENTITY,
            cms_password = SIGNAL_CLIENT_PASSWORD,
            collection_name = "automatica",
            table_name = "airquality_sensor",
        )

        # Client für CO2
        self.co2_client = signal_client.connect_column(
            column_name = "CO₂", unit = "ppm", description = "Carbon Dioxide",
            minimum = 350, maximum = 5000, decimal_places = 0
        )
        self.temp_client = signal_client.connect_column(
            column_name = "Temperature", unit = "°C",
            minimum = 0, maximum = 50, decimal_places = 0
        )
        self.hum_client = signal_client.connect_column(
            column_name = "Relative Humidity", unit = "% rH",
            minimum = 0, maximum = 100, decimal_places = 0
        )
        self.o3_client = signal_client.connect_column(
            column_name = "O₃", unit = "µg/m³", description = "Ozone",
            minimum = 0, maximum = 500, decimal_places = 0
        )
        self.co_client = signal_client.connect_column(
            column_name = "CO", unit = "mg/m³", description = "Carbon Monoxide",
            minimum = 0, maximum = 20, decimal_places = 0
        )
        self.no2_client = signal_client.connect_column(
            column_name = "NO₂", unit = "µg/m₃", description = "Nitrous Dioxide",
            minimum = 0, maximum = 500, decimal_places = 0
        )
        
        print('Connected to airquality database')


    def measurement_cycle(self, vent_time, wait_time, iterations) -> dict:
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

        [con_filtered, con_unfiltered] = self.cozir_co2.read_bulk(iterations=3, delay=0.5)
        [con_o3, temp_o3, hum_o3] = self.ec_o3.read_bulk(iterations=iterations, delay=0.1)
        [con_co, temp_co, hum_co] = self.ec_co.read_bulk(iterations=iterations, delay=0.1)
        [con_no2, temp_no2, hum_no2] = self.ec_no2.read_bulk(iterations=iterations, delay=0.1)

        conv_o3 = 1.96
        conv_co = 1.15
        conv_no2 = 1.88
        
        # remove CO2 bias
        co2_value = con_filtered + self.CO2_BIAS
        if co2_value < 420:
            self.CO2_BIAS += 420 - co2_value
            logging.info(f"Updated CO2 Bias: {self.CO2_BIAS}")

        return {
            self.ec_o3.sensor_type:(con_o3*conv_o3 + self.O3_BIAS), # convert o3 values from ppb to µg/m³
            self.ec_no2.sensor_type:(con_no2*1000)*conv_no2 + self.NO2_BIAS, # convert no2 values from ppm to µg/m³
            self.ec_co.sensor_type:(con_co)*conv_co + self.CO_BIAS, # convert co values from ppm to mg/m³
            self.cozir_co2.sensor_type:con_filtered + self.CO2_BIAS,
            'temperature':(temp_o3 + temp_co + temp_no2)/3,
            'humidity':(hum_o3+ hum_no2+ hum_co)/3
        }


    def measure(self, time_between_cycles):
        """
            Description: measure gas concentration in a loop and save measured values in database
        """
        logging.info("Main    : Starting measurements")

        loop_forever=True
        while loop_forever:
            try:
                execution_started_at = datetime.now().timestamp()

                var = self.measurement_cycle(vent_time=10, wait_time=1, iterations=5)
                self.co2_client.add_datapoint("node_1", var['CO2'])
                self.co_client.add_datapoint("node_1", var['CO'])
                self.no2_client.add_datapoint("node_1", var['NO2'])
                self.o3_client.add_datapoint("node_1", var['O3'])
                self.temp_client.add_datapoint("node_1", var['temperature'])
                self.hum_client.add_datapoint("node_1", var['humidity'])
                
                """
                self.client.insert_data(self._sensor_id, {"no2": var["NO2"]})
                self.client_verbose.insert_data(self._sensor_id,
                                                {"no2" : var["NO2"], "co" : var["CO"], "o3" : var["O3"],
                                                 "temperatur" : var["temperature"],
                                                 "luftfeuchtigkeit" : var["humidity"]})
                """
                # make logging message
                logging.info("New Measurement")
                print("---")
                print("|      NO2    : {0:.2f} µg/m³".format(var['NO2']))
                print("|      O3     : {0:.2f} µg/m³".format(var['O3']))
                print("|      CO     : {0:.2f} mg/m³".format(var['CO']))
                print("|      CO2    : {0:.2f} ppm".format(var['CO2']))
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
