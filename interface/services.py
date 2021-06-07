# import connection_url
import psycopg2
import pyodbc
import pymysql
import cx_Oracle as co

def db_connection(engine, username, password, host, db_name):
    conn = None
    if engine == 'postgres':
    # conn = connection_url.config('{}://{}:{}@{}:{}/{}'.format(engine, username, password, host, port, db_name))
        conn = psycopg2.connect(host=host, database=db_name, user=username, password=password)
    elif engine == 'pymysql':
        conn = pymysql.connect(host=host, user=username, password=password, database=db_name)
    elif engine == 'pyodbc':
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+host+';DATABASE='+db_name+';UID='+username+';PWD='+password)
    elif engine == 'oracle':
        conn_str = u'{}/{}@{}/{}'.format(username, password, host, db_name)  # db_name here stands for service
        conn = co.connect(conn_str)

    return conn


# conn = db_connection('postgres', 'ufazzer0505', '127.0.0.1', 'postgres')
# # conn = psycopg2.connect(user="postgres",
# #                               password="ufazzer0505",
# #                               host="127.0.0.1",
# #                               port="5432",
# #                               database="postgres")
# print(conn)
# cursor = conn.cursor()
#
# cursor.execute("SELECT * FROM persons")
#
# print(cursor.fetchall())
