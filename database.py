#------------------------------------------------------------#
# Helper functions to interact with the SQLITE QRCC Database #
#------------------------------------------------------------#
from sys import exit                      
import sqlite3                               # import the database manager stuff
from urllib.request import pathname2url      # import function to create uri for sqlite

def connectToDatabase(dbname):
    '''Connect to the database and return the connection object

    Arguments:
    dbname - the name of the database 
    Returns:
    a connection to the database or NONE if an error occurs   
    '''
    try:
        dburi = f"file:{pathname2url(dbname)}?mode=rw"
        conn = sqlite3.connect(dburi, uri=True)
    except:
        # database does not exist - bad news 
        print(f"Database: {dbname} not available - cannot establish a connection")
        exit(16)
    return conn

def select(dbname, sqlQuery, values:tuple):
    conn = connectToDatabase(dbname)
    try:
        cursor = conn.cursor()
        cursor.execute(sqlQuery, values)
        results = cursor.fetchall()
        cursor.close()
        return results            
    except sqlite3.Error as e:
        print(f"SQLite error selecting data: {e}") 
        print(f"Query was: {sqlQuery}")
        print(f"Values were: {values}") 
        return None  
    finally:
        if conn:
            conn.close()  
    
def insert(dbname, sqlQuery, values:list):
    conn = connectToDatabase(dbname)
    try:
        cursor = conn.cursor()
        cursor.execute(sqlQuery, values)
        result = "SQL_OK"
        conn.commit()
        return result            
    except sqlite3.Error as e:
        if e.sqlite_errorcode == 2067 or 1555:
            return "SQL_DUPLICATE"
        else:
            print(f"Error Code: {e.sqlite_errorcode}, Error Name: {e.sqlite_errorname}")
            print(f"SQLite error inserting data: {e}") 
            print(f"Query was: {sqlQuery}")
            print(f"Values were: {values}") 
            return None
    finally:
        if conn:
            conn.close()        

def update(dbname, sqlQuery, values:list):
        conn = connectToDatabase(dbname)        
        try:
            cursor = conn.cursor()
            cursor.execute(sqlQuery, values)
            result = "SQL_OK"
            conn.commit()
            return result            
        except sqlite3.Error as e:
           print(f"SQLite error updating data: {e}") 
           print(f"Query was: {sqlQuery}")
           print(f"Values were: {values}") 
           return None  
        finally:
           if conn:
              conn.close()             

def delete(dbname, sqlQuery, values:list):
        conn = connectToDatabase(dbname)    
        try:
            cursor = conn.cursor()
            cursor.execute(sqlQuery, values)
            result = "SQL_OK"
            conn.commit()
            return result            
        except sqlite3.Error as e:
           print(f"SQLite error deleting data: {e}") 
           print(f"Query was: {sqlQuery}")
           print(f"Values were: {values}") 
           return None  
        finally:
           if conn:
              conn.close()              