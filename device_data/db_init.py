'''
Initialize the sqlite3 database of the airquality station.
'''
import sqlite3


def init_db():
    '''
    Method to initialize a sqlite database for the airquality measurement station.
    '''

    try:
        sqlite_connection = sqlite3.connect('airquality.db')
        cursor = sqlite_connection.cursor()
        print('Established connection to SQLite')

        table_no2 = ''' CREATE TABLE NO2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp timestamp NOT NULL,
                    value REAL NOT NULL,
                    unit char(3) NOT NULL,
                    temperature REAL NOT NULL,
                    humidity REAL NOT NULL); 
                '''

        table_o3 = ''' CREATE TABLE O3 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp timestamp NOT NULL,
                    value REAL NOT NULL,
                    unit char(3) NOT NULL,
                    temperature REAL NOT NULL,
                    humidity REAL NOT NULL); 
                '''

        table_co = ''' CREATE TABLE CO (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp timestamp NOT NULL,
                    value REAL NOT NULL,
                    unit char(3) NOT NULL,
                    temperature REAL NOT NULL,
                    humidity REAL NOT NULL); 
                '''
        
        table_co2 = ''' CREATE TABLE CO2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp timestamp NOT NULL,
                    value REAL NOT NULL,
                    unit char(3) NOT NULL,
                    temperature REAL NOT NULL,
                    humidity REAL NOT NULL); 
                '''
       
        cursor.execute(table_no2)
        print('Created table NO2')

        cursor.execute(table_o3)
        print('Created table O3')

        cursor.execute(table_co)
        print('Created table CO')

        cursor.execute(table_co2)
        print('Created table CO2')

        cursor.close()

    except sqlite3.Error as error:
        print('Error while initializing SQlite database', error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print('SQLite connection closed')



if __name__ == "__main__":
    init_db()
