"""
Organization: Professorship of Environmental Sensing and Modelling, TU Munich
Date: 14.04.2022
Author: Daniel Kühbacher

Description: This script reads our sensors and saves the measured values in a
sqlite database.
"""

from concurrent.futures import thread
from socket import timeout
import RPi.GPIO as GPIO
import time
import logging
import sqlite3
import threading

from datetime import datetime
from ecsense import ECSensor

class measure_airquality: 

    def __init__(self, db_path):
        """
            Description: Constructor
            Parameters: db_path: path to sqlite3 database
        """ 
        #set GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(27,GPIO.OUT)

        #init sensors and serial ports
        self.ec1 = ECSensor('/dev/ttyS0') #No2 Sensor
        self.ec2 = ECSensor('/dev/ttyAMA1') #O3 Sensor
        self.ec3 = ECSensor('/dev/ttyAMA2') #CO Sensor

        # connect to database
        self.con = sqlite3.connect(db_path)
        self.cursor = self.con.cursor()
        print('Connected to airquality database')

    def vent_meas_cycle(self, vent_time=6, wait_time=3, iterations=5) -> dict:
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

        #array to save values
        temp=[0,0,0,0,0]
        
        # make i consecutive measurements and calculate average value
        for i in range (0, iterations):
            dat1 = self.ec1.read_sensor()
            dat2 = self.ec2.read_sensor()
            dat3 = self.ec3.read_sensor()
            
            temp[0] = temp[0] + dat1[0]
            temp[1] = temp[1] + dat2[0]
            temp[2] = temp[2] + dat3[0]
            temp[3] = temp[3] + dat1[1]+ dat2[1]+ dat3[1]
            temp[4] = temp[4] + dat1[2]+ dat2[2]+ dat3[2]
            
            time.sleep(0.2) # wait for some short time before executing the next measurement
            
        values = {  self.ec1.sensor_type:(temp[0]/iterations),
                    self.ec2.sensor_type:(temp[1]/iterations),
                    self.ec3.sensor_type:(temp[2]/iterations),
                    'temperature':(temp[3]/(3*iterations)),
                    'humidity':(temp[4]/(3*iterations))}
        
        return values
    
    def measure(self):
        """
            Description: measure gas concentration and save measured values in database
        """  

        dat = self.vent_meas_cycle()
        timestamp = datetime.now()
        
        # insert data to database
        insert_query = """INSERT INTO {} (timestamp, value, unit, temperature, humidity)
                        VALUES(?,?,?,?,?)"""
        
        self.cursor.execute(insert_query.format('NO2'),
                        (timestamp, dat['NO2'], 'ppm',
                        dat['temperature'], dat['humidity']))
        
        self.cursor.execute(insert_query.format('O3'),
                        (timestamp, dat['O3'], 'ppb',
                        dat['temperature'], dat['humidity']))
        
        self.cursor.execute(insert_query.format('CO'),
                        (timestamp, dat['CO'], 'ppm',
                        dat['temperature'], dat['humidity']))
        
        self.con.commit() # safe data in database

        # make logging message
        logging.info("New Measurement")
        print("---")
        print("|      NO2    : {0:.4f} ppm".format(dat['NO2']))
        print("|      O3     : {0:.4f} ppb".format(dat['O3']))
        print("|      CO     : {0:.4f} ppm".format(dat['CO']))
        print("| Temperature : {0:.1f} °C".format(dat['temperature']))
        print("|   Humidity  : {0:.1f} rH".format(dat['humidity']))
        print("---\n")
      
    def __del__(self):
        """
            Description: Destructor; close db connection and cleanup GPIOs
        """ 

        self.con.close()
        GPIO.cleanup()

if __name__ == "__main__":

    print('Air quality measurement station v1.1 (no GUI)')
    print('Press Ctrl+C to close the program...')

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    #### Start of the measurements
    print('\n\nStart logging...')
    logging.info("Main    : Starting measurements.")

    measurement_obj = measure_airquality(db_path = 'device_data/airquality.db')

    loop_forever = True
    while loop_forever:
        try:
            measurement_obj.measure()
            time.sleep(30)
        except KeyboardInterrupt:
            loop_forever = False

    del measurement_obj
    #### End of Measurements

    print("Program end") 