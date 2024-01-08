import os
import sqlite3 as sql
import json
import time as sleep


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

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS imuSensors( Data_Type TEXT,Reading_Value REAL,Timestamps INTEGER )""")
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS regularSensors( Data_Type TEXT, Reading_Value REAL , Timestamps INTEGER )""")
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS averageData( Data_Type TEXT, Reading_Value_Average REAL , Timestamps INTEGER )""")



def get_table_name(reading_header):
    imu_header_name = ["imu"]
    regular_header_name = ["timestamp", "dht", "bme", "anemometer", "gps"]
    table_name = None

    if reading_header in imu_header_name:
        table_name = "imuSensors"
    elif reading_header in regular_header_name:
        table_name = "regularSensors"

    return table_name

def update_regular_table( connection,data_type,reading_value, reading_time):
          cursor = connection.cursor()


          add_row_sql = ''' INSERT INTO regularSensors(Data_Type,Reading_Value,Timestamps)
                       VALUES(?,?,?) '''
          cursor.execute(add_row_sql, (data_type, reading_value,reading_time))
          connection.commit()
          print("Updated table")


def update_imu_table(connection, data_type, reading_value, reading_time):
    cursor = connection.cursor()

    add_row_sql = ''' INSERT INTO imuSensors(Data_Type, Reading_Value,Timestamps)
                     VALUES(?,?,?) '''

    for item in reading_value:
        cursor.execute(add_row_sql, (data_type, item , reading_time))
        connection.commit()
    print("Updated table")

def update_average_table(connection, data_type, reading_time):
    cursor = connection.cursor()

    add_row_sql = ''' INSERT INTO averageData(Data_Type, Reading_Value_Average,Timestamps)
                  VALUES(?,?,?) '''

    get_previous_sql = '''SELECT Reading_Value FROM regularSensors WHERE Data_Type = ?'''
    cursor.execute(get_previous_sql, (data_type,))
    connection.commit()
    previous_value_list = list(cursor.fetchall())
    connection.commit()
    previous_values = []
    for item in previous_value_list:

        for value in item:
            print(value)
            previous_values.append(value)

    print(len(previous_values))
    average_value = sum(previous_values) / len(previous_values)
    print("Average Value")
    print(average_value)


    cursor.execute(add_row_sql, (data_type, average_value , reading_time))
    connection.commit()
    print("Updated table")


def calculate_time(json_file, data_type, data_header):
    number_of_readings = len(json_file[data_header][data_type])
    reading_frequency = 1 / number_of_readings
    return reading_frequency
def parse_data(connection, json_data):
    cursor = connection.cursor()
    make_average_data = ["dht_temp", "dht_humidity", "bme_temp", "bme_humidity", "bme_pressure", "ppm", "airQuality", "windSpeed", "speed"]

    for dataHeaders in json_data:
        reading_header = dataHeaders
        table_name = get_table_name(reading_header)
        if table_name is not None:
            for dataType in json_data[dataHeaders]:
                reading_frequency = calculate_time(json_data, dataType, reading_header)
                package_time = json_data["timestamp"]["time"][0]
                for reading_value in json_data[dataHeaders][dataType]:
                    package_time -= reading_frequency
                    if(table_name == "regularSensors"):
                        update_regular_table( connection, dataType, reading_value, package_time)
                        if dataType in make_average_data:
                            update_average_table(connection, dataType, package_time)
                    elif(table_name == "imuSensors"):
                        update_imu_table( connection,  dataType, reading_value, package_time)




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

    while 1 == 1:
        jsonFile = open("dummyReadingsJSON.json")
        jsonData = json.load(jsonFile)

        parse_data(connection, jsonData)
        sleep.sleep(1)

if __name__ == '__main__':
    main()
