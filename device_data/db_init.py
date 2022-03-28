'''
short script to initialize sqlite3 database
'''
import sqlite3


def init_db():
    try:
        sqliteConnection = sqlite3.connect('airquality.db')
        cursor = sqliteConnection.cursor()
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
        cursor.execute(table_no2)
        print('Created table NO2')
        
        cursor.execute(table_o3)
        print('Created table O3')
        
        cursor.execute(table_co)
        print('Created table CO')
        
        cursor.close()

    except sqlite3.Error as error:
        print('Error while initializing SQlite', error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print('SQLite connection closed')
    
if __name__=="__main__":
    init_db()