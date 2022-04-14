"""
Organization: Professorship of Environmental Sensing and Modelling, TU Munich
Date: 14.03.2022
Author: Daniel Kühbacher

Description: This script reads our sensors and saves the measured values in a
sqlite database.
"""

import RPi.GPIO as GPIO
import time
import logging
import sqlite3

import threading as th
from datetime import datetime
from ec_sense import ec_sensor

#set GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(27,GPIO.OUT)

#init sensors and serial ports
ec1 = ec_sensor('/dev/ttyS0') #No2 Sensor
ec2 = ec_sensor('/dev/ttyAMA1') #O3 Sensor
ec3 = ec_sensor('/dev/ttyAMA2') #CO Sensor

#main thread with while loop
def measure_airquality(db_connection, vent_time=5, wait_time=2):
    """
        Description: main function for measuring air quality
        Paramerters: db_connection - database connection object
                     interval - sleep time between two consecutive measurements
        Return: list of averaged sensor values in the following order: gas, temperature, humidity
    """

    # connect to database
    cursor = db_connection.cursor()
    
    dat = vent_meas_cycle(vent_time, wait_time)
    timestamp = datetime.now()
    
    # insert data to database
    insert_query = """INSERT INTO {} (timestamp, value, unit, temperature, humidity)
                    VALUES(?,?,?,?,?)"""
    
    cursor.execute(insert_query.format('NO2'),
                    (timestamp, dat['NO2'], 'ppm',
                    dat['temperature'], dat['humidity']))
    
    cursor.execute(insert_query.format('O3'),
                    (timestamp, dat['O3'], 'ppb',
                    dat['temperature'], dat['humidity']))
    
    cursor.execute(insert_query.format('CO'),
                    (timestamp, dat['CO'], 'ppm',
                    dat['temperature'], dat['humidity']))
    
    db_connection.commit() # safe data in database

    # make logging message
    logging.info("Measurement : NO2: %f ppm | O3: %f ppb | CO: %f ppm", dat['NO2'], dat['O3'], dat['CO'])


def vent_meas_cycle(vent_time=3, wait_time=3, iterations=1):

    # ventilate channel 
    GPIO.output(27,True)
    time.sleep(vent_time)
    GPIO.output(27,False)
    time.sleep(wait_time)

    #array to save values
    temp=[0,0,0,0,0]
    
    # make i consecutive measurements and calculate average value
    for i in range (1, iterations):
        dat1 = ec1.read_sensor()
        dat2 = ec2.read_sensor()
        dat3 = ec3.read_sensor()
        
        temp[0] = temp[0] + dat1[0]
        temp[1] = temp[1] + dat2[0]
        temp[2] = temp[2] + dat3[0]
        temp[3] = temp[3] + dat1[1]+dat2[1]+dat3[1]
        temp[4] = temp[4] + dat1[2]+dat2[2]+dat3[2]
        
        time.sleep(0.1)
        
    values = {ec1.sensor_type:(temp[0]/iterations),
              ec2.sensor_type:(temp[1]/iterations),
              ec3.sensor_type:(temp[2]/iterations),
              'temperature':(temp[3]/(3*iterations)),
              'humidity':(temp[4]/(3*iterations))}
    
    return values

if __name__ == "__main__":

    print('Air quality measurement station v1.1 (no GUI)')
    con = sqlite3.connect('device_data/airquality.db')
    print('Connected to airquality database')
    print('Press any key to close the program...')

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    #### Start of the measurements
    logging.info("Main    : Starting measurements.")

    measure_airquality(con)

    #commit data and close the database
    con.close()
    GPIO.cleanup()
    
    print("Program end") 