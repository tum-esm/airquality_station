import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3

con = sqlite3.connect('/home/pi/Documents/code/airq_pc/data/airquality.db')

no2 = pd.read_sql_query("SELECT * from NO2",con)

no2['datetime'] = pd.to_datetime(no2['timestamp'])

no2.drop(['timestamp', 'id'], axis = 1, inplace=True)

print(no2.head())