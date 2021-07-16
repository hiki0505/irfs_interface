# import connection_url
import psycopg2
import pyodbc
import pymysql
import cx_Oracle as co

def db_connection(engine, username, password, host, db_name):
    conn = None
    if engine == 'postgres':
        conn = psycopg2.connect(host=host, database=db_name, user=username, password=password)
    elif engine == 'pymysql':
        conn = pymysql.connect(host=host, user=username, password=password, database=db_name)
    elif engine == 'pyodbc':
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+host+';DATABASE='+db_name+';UID='+username+';PWD='+password)
    elif engine == 'oracle':
        conn_str = u'{}/{}@{}/{}'.format(username, password, host, db_name)  # db_name here stands for service
        conn = co.connect(conn_str)

    return conn
