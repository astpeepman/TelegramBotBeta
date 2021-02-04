import sqlite3 as sql
from sqlite3 import Error
from src.Modules.InfoModule import *


#База данных
DB = 'src/MainDB.db'

def create_connection():
    connection = None
    try:
        connection = sql.connect(DB, check_same_thread = False)
    except Error as e:
        print('DB::connection to error', f"The error '{e}' occurred")

    return connection

connection = create_connection()

def execute_query(query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        return cursor.lastrowid
    except Exception as e:
        print('DB::query error', e)

def execute_read_query(query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print('DB::read error', f"The error '{e}' occurred")


def SelectInTable(table, selObject='*', equal=None, condition=None):
    if equal is not None and condition is not None:
        getQuery = f"SELECT {selObject} from {table} WHERE `{equal}`=='{condition}'"
    else:
        getQuery = f"SELECT {selObject} from `{table}`"

    return execute_read_query(getQuery)

def GetColumnsNames(table):
    cursor=connection.execute('select * from '+str(table))
    names=list(map(lambda x:x[0], cursor.description))
    return names