import pyodbc
import os

SERVER_NAME = os.environ['EverleapServerName']
DATABASE_NAME = os.environ['EverleapDatabase']
SERVER_USER_ID = os.environ['EverleapUserId']
SERVER_PASSWORD = os.environ['EverleapPassword']

conn = pyodbc.connect('Driver={SQL Server};'
                      f'Server={SERVER_NAME};'
                      f'Database={DATABASE_NAME};'
                      f'UID={SERVER_USER_ID};'
                      f'PWD={SERVER_PASSWORD};'
                      f'Integrated_Security=no;')

cursor = conn.cursor()

cursor.execute("SELECT @@version;") 
row = cursor.fetchone() 
while row: 
    print(row[0])
    row = cursor.fetchone()