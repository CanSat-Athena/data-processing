import sqlite3 as sql
import matplotlib.pyplot as plt
import numpy as np



def create_connection(database_name):
    conn = None

    try:
        conn = sql.connect(database_name)
        return conn
    except sql.Error as e:
        print(e)
        return conn


def draw_reading_time_graph(conn):
    cursor = conn.cursor()
    x_data = ""
    y_data = ""
    x_values = []
    y_values = []
    x_label = ""
    y_label = ""
    graph_title = ""
    x_data = input("Enter x-axis data:")

    get_reading_values_sql = '''SELECT Reading_Value FROM regularSensors where Data_Type = ?'''
    get_time_values_sql = '''SELECT Timestamps from RegularSensors where Data_Type = ?'''
    cursor.execute(get_reading_values_sql, (x_data,))
    y_values = cursor.fetchall()
    cursor.execute(get_time_values_sql, (x_data,))
    x_values = cursor.fetchall()
    for i in y_values:
        print(i)
    plt.scatter(x_values, y_values)
    plt.show()


def main():

    database_name = "CanSatDatabase.db"
    conn = create_connection(database_name)
    if conn is not None:
        print("Connected to Database!")
        draw_reading_time_graph(conn)
    else:
        print("Error! Could not connect to Database")

if __name__ == "__main__":
    main()