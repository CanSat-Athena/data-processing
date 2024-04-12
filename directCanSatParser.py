from multiprocessing import Pool
import sqlite3 as sql
import csv as csv
import math as math
import imufusion as imufusion
import numpy as np
import os as os
from tkinter import *


get_time = lambda fn: os.path.getmtime(fn)

true = True
false = False       #                                                             g   degPerSecond ut                      
                    #msSinceBoot,dhtTemp,dhtHum,bmeTemp,bmeHum,bmePres,bmeGaRe,imuAccel,imuGyro,imuMag,Light,Wind,lat,long,alt,gpsTime,gpsFix,batVolt,batPerc,fsUsa,fsSize,RSSI
transmitted_data_list = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
no_items_in_section = [1,2,4,9,1,1,7]
transimtted_data_place_in_array = [[0],[1,2],[3,4,5,6],[7,7,7,8,8,8,9,9,9],[10],[11],[12,13,14,15,15,15,16]]
time_offsetter = 0

def create_db_connection():
    conn = sql.connect("cansatReadingsDirect.db")
    return conn

def create_tables(conn):
    cur = conn.cursor()
    
    cur.execute("CREATE TABLE IF NOT EXISTS imuReadings(name TEXT, value REAL, timestamp REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS regularReadings(name TEXT, value REAL, timestamp REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS gpsReadings(name TEXT, value REAL, timestamp REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS averageReadings(name TEXT, value REAL, timestamp REAL)")
    conn.commit()


fn = 'cansatReadings.csv'
prev_time = get_time(fn)
connection = create_db_connection()
create_tables(connection)



accel_offset = [0,0,0]
gyro_offset = [0,0,0]
mag_offset = [0,0,0]

accel_calibrating_values = [[],[],[]]
gyro_calibrating_values = [[],[],[]]


is_calibrating_imu = false
imu_calibrate_counter = 0

last_ms = 0
offset = 0


lines_parsed = 0
line_counter = 0
final_converted_list = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
final_converted_list_names = ["timestamp", "dhtTemp", "dhtHum", "bmeTemp", "bmeHum", "bmePres", "bmeGasRe", "imuAccel", "imuGyro", "imuMag", "eulerAngle", "ldrVoltage", "ldrLux", "ldrSolarIraddiance", "windTriggers", "windSpeed", "windSpeed90", "lat", "long", "alt", "fix","alt_calc"] 
running_average_list = ["dhtTemp", "dhtHum", "bmeTemp", "bmeHum", "bmePres", "bmeGasRe","ldrVoltage", "ldrLux", "ldrSolarIraddiance", "windTriggers", "windSpeed", "windSpeed90"]

root = Tk()
root.geometry("100x100")

def calibrate_imu():
    global is_calibrating_imu
    is_calibrating_imu = true

imu_calbrator_button = Button(root,text = "Calibrate IMU", command = calibrate_imu)
imu_calbrator_button.grid()

def ldr_voltage_to_lux(voltage_transmitted):
    lux = 0
    if voltage_transmitted != "":
        voltage  = (float(voltage_transmitted)/4095) * 3.3
        resistance = voltage/2 
        lux = resistance * 10
    return lux

def lux_to_solar_irradiance(lux):
    solar_irradiance = lux * 0.0079
    return solar_irradiance

def ahrs_algorithim(gyroscope_data, accelerometer_data):
    ahrs = imufusion.Ahrs()
    euler_angle = np.empty((1,3))
    
    accelerometer_data_c = []
    gyr_data_c =[]
    
    for i in range(0,3):
        if gyroscope_data[i] != '':
         gyr_data_c.append( float(gyroscope_data[i]))
    for i in range(0,3):
        if accelerometer_data[i] != '' :
             accelerometer_data_c.append( float(accelerometer_data[i]))
    accelerometer_data_c = np.array(accelerometer_data_c)
    gyr_data_c = np.array(gyr_data_c)
    
    ahrs.update_no_magnetometer(gyr_data_c, accelerometer_data_c, 1 )   
    euler_angle[0] = ahrs.quaternion.to_euler()
    return euler_angle[0]

def logarithmic_sheer(low_down_wind_speed,wanted_height):
    new_velocity = low_down_wind_speed * ((math.log((0.106)/(0.03)))/(math.log((wanted_height)/(0.03))))
    return new_velocity

def hall_effect_sensor_to_wind_speed(triggers): 
    rotations = float(triggers[0])/3
    distance_travelled = rotations * 34.34
    time_taken = 124
    speed =  distance_travelled/time_taken
    return speed

def calculate_altitude(air_pressure):
    alt_feet = ((10**((math.log10(float(air_pressure)/1013.25))/(5.2558797)))-1)/(-6.8755856 * 10**6)
    alt_met = alt_feet/3.281
    return alt_met

def update_imu_table(name, value,time,conn):
    cursor = conn.cursor()
    sql = "INSERT INTO imuReadings(name, value, timestamp) VALUES (?,?,?)"
    cursor.execute(sql,(name,value,time))
    conn.commit()

def update_regular_table(name, value,time,conn):
    cursor = conn.cursor()
    sql = "INSERT INTO regularReadings(name, value, timestamp) VALUES (?,?,?)"
    cursor.execute(sql,(name,value,time))
    conn.commit()
    
def update_average_table(name, time,conn):
    cursor = conn.cursor()
    sql = "INSERT INTO averageReadings(name, value, timestamp) VALUES (?,?,?)"
    previous_values = []
    average_value = 0
    cursor.execute("SELECT value from regularReadings where name=?", (name,))
    previous_values = cursor.fetchall()
    average_value = sum(previous_values[0])/len(previous_values)
    cursor.execute(sql,(name, average_value, time))
    conn.commit()
    
def update_gps_table(name,value, time, conn):
    cursor = conn.cursor()
    sql = "INSERT INTO gpsReadings(name, value, timestamp) VALUES (?,?,?)"
    cursor.execute(sql,(name,value,time))
    conn.commit()


def convert_data(row_as_list,conn):
    
    global last_ms
    global offset
    
    if int(row_as_list[0][0]) < last_ms:
        offset = last_ms
    row_as_list[0][0] = int(row_as_list[0][0])
    row_as_list[0][0] += offset
    last_ms = row_as_list[0][0]
    
   

    for i in range(0, len(row_as_list[7])):
       if row_as_list[7][i] != '': 
        row_as_list[7][i] = float(row_as_list[7][i])
        row_as_list[7][i]-=accel_offset[i%3]
    for i in range(0, len(row_as_list[8])):
       if row_as_list[7][i] != '': 
        row_as_list[8][i] = float(row_as_list[8][i])
        row_as_list[8][i]-=accel_offset[i%3]

    
    altitude_list = []
    for pressure in row_as_list[5]:
        altitude_list.append(calculate_altitude(pressure))
    wind_speed = []
    wind_speed_at_90 = []
    wind_speed.append(hall_effect_sensor_to_wind_speed(row_as_list[11]))
    wind_speed_at_90.append(logarithmic_sheer(wind_speed[0],90))
    euler_angles = ahrs_algorithim(row_as_list[7], row_as_list[8]).tolist()
    lux_list = []
    for voltage in row_as_list[10]:
        lux_list.append(ldr_voltage_to_lux(voltage))
    solar_irradiance_list = []
    for lux in lux_list:
        solar_irradiance_list.append(lux_to_solar_irradiance(lux))
    
    for i in range(0,10):
        final_converted_list[i] = row_as_list[i]
    final_converted_list[10] = euler_angles
    final_converted_list[11] = row_as_list[10]
    final_converted_list[12] = lux_list
    final_converted_list[13] = solar_irradiance_list
    final_converted_list[14] = row_as_list[11]
    final_converted_list[15] = wind_speed
    final_converted_list[16] = wind_speed_at_90
    final_converted_list[17] = row_as_list[12]
    final_converted_list[18] = row_as_list[13]
    final_converted_list[19] = row_as_list[14]
    final_converted_list[20] = row_as_list[16]
    final_converted_list[21] = altitude_list
    
    for i in range(0, len(final_converted_list)):
        if i > 0 and i < 7:
            if i == 1 or i == 2 or i == 3 or i == 4:
                for data in final_converted_list[i]:
                  if data != '':  
                    if float(data) < 100 and float(data) > -10:
                         update_regular_table(final_converted_list_names[i], float(data), final_converted_list[0][0],conn)
            else:
                for data in final_converted_list[i]:
                  if data != '':  
                    update_regular_table(final_converted_list_names[i], float(data), final_converted_list[0][0],conn)
        if i > 6 and i < 10:
            for data in final_converted_list[i]:
               if data != '':   
                update_imu_table(final_converted_list_names[i], float(data),final_converted_list[0][0],conn)
        if i > 9 and i < 17:
             for data in final_converted_list[i]:
               if data != '':    
                update_regular_table(final_converted_list_names[i], float(data), final_converted_list[0][0],conn)
        if i > 16 and i < 21:
            for data in final_converted_list[i]:
               if data != '':   
                update_gps_table(final_converted_list_names[i], float(data), final_converted_list[0][0],conn)
        if i == 21:
            for data in final_converted_list[i]:
               if data != '':   
                update_regular_table(final_converted_list_names[i], float(data), final_converted_list[0][0],conn)

        if final_converted_list_names[i] in running_average_list:
            update_average_table(final_converted_list_names[i], final_converted_list[0][0], conn)
        
    return 0

def is_malprinted_row_pre_check(row):
    has_all_brackets = false
    bracket_counter = 0
    for character in row:
        if '[' in character:
            bracket_counter+=1
        if ']' in character:
            bracket_counter+=1
    if bracket_counter == 14:
        has_all_brackets = true
    print(has_all_brackets)
    return not has_all_brackets


    

def is_malprinted_row_post_check(row_as_list):
    in_range = false
    has_all_data = true
    
    for data in row_as_list[7]:
      if data != '':  
        if data.count('.') != 1:
            has_all_data = false
    for data in row_as_list[8]:
       if data != '':  
        if data.count('.') != 1:
            has_all_data = false
    for data in row_as_list[9]:
       if data != '': 
        if data.count('.') != 1:
            has_all_data = false
    
    

    
    dht_items = len(row_as_list[1]) + len(row_as_list[2])
    bme_items = len(row_as_list[3]) + len(row_as_list[4])  + len(row_as_list[5]) + len(row_as_list[6])
    imu_items = len(row_as_list[7]) + len(row_as_list[8]) + len(row_as_list[9])
    gps_tems = len(row_as_list[12]) + len(row_as_list[13]) + len(row_as_list[14]) + len(row_as_list[15]) + len(row_as_list[16])

    
    print(dht_items)
    print(bme_items)
    print(imu_items)
    print(gps_tems)
   
    
    if dht_items % 2 != 0 or bme_items % 4 != 0 or (imu_items - 1 ) % 9 != 0 or gps_tems % 7 !=0:
        has_all_data = false
    print(has_all_data)
    return not has_all_data

    
    
def get_transmitted_data_index(section_counter, item_in_section_counter):
    place_in_data_set = item_in_section_counter%no_items_in_section[section_counter]
    return transimtted_data_place_in_array[section_counter][place_in_data_set]

def parse_row(row):
    global line_counter
    global lines_parsed
    global connection
    print("Line Counter: " + str(line_counter))
    print("Lines Counted: " + str(lines_parsed))
    if not is_malprinted_row_pre_check(row):   
        sensor_counter = -1
        item_in_section_counter = -1
        for character in row:
            if '[' in character:
                sensor_counter+=1
                character = character[1:]
                item_in_section_counter = -1
            item_in_section_counter+=1
            if ']' in character:
                character = character[:-1]  
            array_index = get_transmitted_data_index(sensor_counter, item_in_section_counter)
            transmitted_data_list[array_index].append(character)
        if not is_malprinted_row_post_check(transmitted_data_list):
            convert_data(transmitted_data_list,connection)
            for data_set in transmitted_data_list:
                data_set.clear()
            print(transmitted_data_list)
        for data_set in transmitted_data_list:
                data_set.clear()
        lines_parsed+=1
    line_counter+=1


def parse_file(file_to_parse):
        csv_reader = csv.reader(file_to_parse)
        global lines_parsed
        global line_counter
        line_counter = lines_parsed

        for row in list(csv_reader)[lines_parsed:]:
            parse_row(row)

if __name__ == '__main__':
    while True:
        root.update()
        t = get_time(fn)
        if t != prev_time:
            with open("cansatReadings.csv ", 'r') as readings_file:
                parse_file(readings_file)
                print("Parsed")
            prev_time = t


  
