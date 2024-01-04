import os
import sqlite3 as sql
import json


def make_database(database_name):
    conn = None

    try:
        conn = sql.connect(database_name)
        return conn
    except sql.Error as e:
        print(e)
        return conn


def does_database_exist(file_name):
    data_base_exists = False

    if os.path.isfile(file_name):
        data_base_exists = True
    return data_base_exists


def create_table(connection):
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS imuSensors (id INTEGER Data_Type INT readingGroup INT  Reading_Value REAL Timestamp INTEGER )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS regularSensors (id INTEGER Data_Type INT Reading_Value REAL Timestamp INTEGER )""")


def main():
    data_base_name = "CanSatDatabase.db"
    connection = None

    if not does_database_exist(data_base_name):
        connection = make_database(data_base_name)
        print("Database Made!")
    else:
        print("Database Found!")
        connection = sql.connect(data_base_name)
    if connection is not None:
        create_table(connection)


if __name__ == '__main__':
    main()
