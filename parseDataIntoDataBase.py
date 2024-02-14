import sqlite3 as sql
import json as json

def get_table_name(sensor_type):
    regular_sensors = ["dht", "bme", "anemometer", "gps", "computed"]
    for regular_sensor_name in  regular_sensors: 
        if sensor_type == regular_sensor_name:
            return "Regular Table"
    return "IMU Table"


def updateAverageTable(reading_type, conn, timestamp):
     cursor = conn.cursor()
     add_row_sql = ''' INSERT INTO Average_Readings(Reading_Name, Reading_Value,Timestamp)
                  VALUES(?,?,?) '''

     get_previous_sql = '''SELECT Reading_Value FROM Regular_Sensors WHERE Reading_Name = ?'''
     cursor.execute(get_previous_sql, (reading_type,))
     conn.commit()
     previous_value_list = list(cursor.fetchall())
     conn.commit()

     previous_values = []
     for items in previous_value_list:
        for item in items:
          previous_values.append(item)
     averageValue = sum(previous_values)/len(previous_values)

     cursor.execute(add_row_sql, (reading_type, averageValue, timestamp))
          

def updateRegularTable(reading_type, reading_value, timestamp, reading_seperation_accounter, conn):
          cursor = conn.cursor()

          add_row_sql = ''' INSERT INTO Regular_Sensors(Reading_Name,Reading_Value,Timestamp)
                       VALUES(?,?,?) '''
          cursor.execute(add_row_sql, (reading_type, reading_value,timestamp - reading_seperation_accounter))
          conn.commit()
          print("Updated table")

def updateIMUTable(reading_type, reading_value, timestamp, reading_seperation_accounter, conn, json_data, sensor_type):
          cursor = conn.cursor()

          add_row_sql = ''' INSERT INTO IMU_Sensors(Reading_Name,Reading_Value,Timestamp)
                       VALUES(?,?,?) '''
          print(reading_value)
          print("H")
          for value in reading_value:
             print(value)
             cursor.execute(add_row_sql, (reading_type, value,timestamp - reading_seperation_accounter))
             conn.commit()
             print("Updated table")


def calculate_seperation_time(reading_type):
    json_frequency = 1000
    seperation_time = json_frequency/len(reading_type)
    return seperation_time

def parse_data(conn, json_file, numberOfObjectsParsed):    

    table_name = ""
    timestamp = int
    reading_seperation = int
    reading_seperation_accounter = 0

    make_average_data = ["dht_temp", "dht_humidity", "bme_temp", "bme_humidity", "bme_pressure", "ppm", "airQuality", "windSpeed", "speed"]

    
    timestamp = json_file[numberOfObjectsParsed]["timestamp"]["time"][0]
    for sensor_type in json_file[numberOfObjectsParsed]:
        table_name = get_table_name(sensor_type)
            
        for reading_type in json_file[numberOfObjectsParsed][sensor_type]:
            reading_seperation = calculate_seperation_time(reading_type)
            print(reading_type)
            for reading_value in json_file[numberOfObjectsParsed][sensor_type][reading_type]:
                    reading_seperation_accounter += reading_seperation
                    if table_name == "Regular Table":
                        updateRegularTable(reading_type, reading_value, timestamp, reading_seperation_accounter, conn)
                    elif reading_type != "time":
                        print(reading_value)
                        updateIMUTable(reading_type, reading_value, timestamp, reading_seperation_accounter, conn,sensor_type)
                    if reading_type in make_average_data:
                         updateAverageTable(reading_type,conn,timestamp)

    
def connect_to_database(database_name):

    conn = None

    try: 
        conn = sql.connect(database_name)
        return conn
    except sql.Error as e:
        print(e)
        return conn

def create_table(conn):

    cur = conn.cursor()

    sql_command_IMU = '''CREATE TABLE IF NOT EXISTS IMU_Sensors(Reading_Name TEXT, Reading_Value REAL, Timestamp INT)'''
    sql_command_Regular = '''CREATE TABLE IF NOT EXISTS Regular_Sensors(Reading_Name TEXT, Reading_Value REAL, Timestamp INT)'''
    sql_command_Average = '''CREATE TABLE IF NOT EXISTS Average_Readings(Reading_Name TEXT, Reading_Value REAL, Timestamp INT)'''

    cur.execute(sql_command_IMU)
    cur.execute(sql_command_Regular)
    cur.execute(sql_command_Average)
    
    conn.commit()
    print("Tables Found/Created")
    

def main():

    numberOfObjectsParsed = 0

    json_file = open("dummyReadings.json")
    json_data = json.load(json_file)
    conn = connect_to_database("cansatReadings.db")
    create_table(conn)
    parse_data(conn, json_data)


if __name__ == '__main__':
    main()   
