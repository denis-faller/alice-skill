import mysql.connector
from mysql.connector import Error

def createConnection(hostName, userName, userPassword, port):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=hostName,
            user=userName,
            passwd=userPassword,
            port=port
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def createDatabase(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as e:
        print(f"The error '{e}' occurred")
        
def useDatabase(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database use successfully")
    except Error as e:
        print(f"The error '{e}' occurred")
        
def createTable(connection, query, tableName):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print(f"Table '{tableName}' created successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def insertRow(connection, query, tableName):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print(f"In table '{tableName}' added data sucessfully")
    except Error as e:
        print(f"The error '{e}' occurred")
        
def updateRow(connection, query, tableName):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print(f"In table '{tableName}' updated data sucessfully")
    except Error as e:
        print(f"The error '{e}' occurred")        

def selectRows(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
        return -1
        
def dropDatabase(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database drop successfully")
    except Error as e:
        print(f"The error '{e}' occurred")        
