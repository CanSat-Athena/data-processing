from multiprocessing import Pool
import sqlite3 as sql
import csv as csv
import math as math
import imufusion as imufusion
import numpy as np
import os as os
import sys as sys
from tkinter import *


get_time = lambda fn: os.path.getmtime(fn)

true = True
false = False       #                                                             g   degPerSecond ut                      
                    #msSinceBoot,dhtTemp,dhtHum,bmeTemp,bmeHum,bmePres,bmeGaRe,imuAccel,imuGyro,imuMag,Light,Wind,lat,long,alt,gpsTime,gpsFix,batVolt,batPerc,fsUsa,fsSize,RSSI
transmitted_data_list = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
no_items_in_section = [1,2,4,9,1,1,7,2,2,1]
transimtted_data_place_in_array = [[0],[1,2],[3,4,5,6],[7,7,7,8,8,8,9,9,9],[10],[11],[12,13,14,15,15,15,16],[17,18],[19,20],[21]]
time_offsetter = 0

def create_db_connection():
    conn = sql.connect("cansatReadings.db")
    return conn

def create_tables(conn):
    cur = conn.cursor()
    
    cur.execute("CREATE TABLE IF NOT EXISTS imuReadings(name TEXT, value REAL, timestamp REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS regularReadings(name TEXT, value REAL, timestamp REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS gpsReadings(name TEXT, value REAL, timestamp REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS averageReadings(name TEXT, value REAL, timestamp REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS baseLineReadings(name TEXT, value REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS flightChecks(name TEXT, hasHappened BOOL, timestamp REAL)")

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
final_converted_list = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
final_converted_list_names = ["timestamp", "dhtTemp", "dhtHum", "bmeTemp", "bmeHum", "bmePres", "bmeGasRe", "imuAccel", "imuGyro", "imuMag", "eulerAngle", "ldrVoltage", "ldrLux", "ldrSolarIraddiance", "windTriggers", "windSpeed", "windSpeed90", "lat", "long", "alt", "fix", "batVolt", "batPerc", "fsUsa", "fsSize", "RSSI","alt_calc"] 
running_average_list = ["dhtTemp", "dhtHum", "bmeTemp", "bmeHum", "bmePres", "bmeGasRe","ldrVoltage", "ldrLux", "ldrSolarIraddiance", "windTriggers", "windSpeed", "windSpeed90"]

root = Tk()
root.geometry("100x100")

def calibrate_imu():
    global is_calibrating_imu
    is_calibrating_imu = true

imu_calbrator_button = Button(root,text = "Calibrate IMU", command = calibrate_imu)
imu_calbrator_button.grid()

def ldr_voltage_to_lux(voltage_transmitted):
    if voltage_transmitted != "":
        voltage_transmitted = int(voltage_transmitted)
        actual_voltage = (voltage_transmitted/4095) * 3.3
        r_2 = 7450
        if actual_voltage != 0:
            resistance = (3.3*(r_2)-actual_voltage*(r_2))/actual_voltage
            lux = (pow((math.exp(11.7)/resistance), 1/(0.623)))
        return lux
    return 0

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
    new_velocity = low_down_wind_speed * ((math.log((0.0000106)/(0.03)))/(math.log((wanted_height/1000)/(0.03))))
    return new_velocity

def hall_effect_sensor_to_wind_speed(triggers): 
    time_difference = (transmitted_data_list[0][0] - last_ms)/1000
    if triggers != "":
        rotational_speed = int(triggers) * (60/time_difference)
        wind_speed_ms = 0.007*(rotational_speed) + 0.22
        wind_speed_kh = (wind_speed_ms*3600)/1000
    
    return wind_speed_kh

def calculate_altitude(air_pressure):
    base_pres = 0
    if air_pressure != "":
        air_pressure = float(air_pressure)
        db = sql.connect("cansatReadings.db")
        curr = db.cursor()
        curr.execute("SELECT value FROM baseLineReadings where name = 'basePressure'")
        base_pres = curr.fetchone()
        if base_pres != None:
             alt_met = (44330 * (1 - ((air_pressure)/(base_pres))**0.1903))
             return alt_met
    return 0
def update_imu_table(name, value,time,conn):
    cursor = conn.cursor()
    sql = "INSERT INTO imuReadings(name, value, timestamp) VALUES (?,?,?)"
    cursor.execute(sql,(name,value,time))
    conn.commit()

def update_baseline_table(name, value,conn):
    cursor = conn.cursor()
    sql = "INSERT INTO baseLineReadings(name, value) VALUES (?,?)"
    cursor.execute(sql,(name,value))
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
    
    
    global is_calibrating_imu
    if is_calibrating_imu:
        alt = row_as_list[14][0]
        pressure = row_as_list[5][0]
        for i in range(0, len(row_as_list[7])):
          if row_as_list[7][i] != '':
            accel_calibrating_values[i%3].append(float(row_as_list[7][i]))
        for i in range(0, len(row_as_list[7])):
           if row_as_list[7][i] != '': 
            accel_calibrating_values[i%3].append(float(row_as_list[7][i]))
        for i in range(0,3):
           if row_as_list[7][i] != '':    
             if len(accel_calibrating_values[i]) != 0: 
                accel_offset[i] = sum(accel_calibrating_values[i])/len(accel_calibrating_values[i])
        for i in range(0,3):
          if row_as_list[7][i] != '':  
             if len(gyro_calibrating_values[i]) != 0: 
                gyro_offset[i] = sum(gyro_calibrating_values[i])/len(gyro_calibrating_values[i])
        update_baseline_table("accelXOffset", accel_offset[0],conn)
        update_baseline_table("accelYOffset", accel_offset[1],conn)
        update_baseline_table("accelZOffset", accel_offset[2],conn)
        update_baseline_table("gyroXOffset", gyro_offset[0],conn)
        update_baseline_table("gyroYOffset", gyro_offset[1],conn)
        update_baseline_table("gyroZOffset", gyro_offset[2],conn)
        update_baseline_table("baseAltitude", alt,conn)
        update_baseline_table("basePressure", pressure,conn)
        
        
        is_calibrating_imu = false    

    for i in range(0, len(row_as_list[7])):
          if row_as_list[7][i] != "" : 
            row_as_list[7][i] = float(row_as_list[7][i])
            row_as_list[7][i]-=accel_offset[i%3]
    for i in range(0, len(row_as_list[8])):
          if row_as_list[8][i] != "" :   
            row_as_list[8][i] = float(row_as_list[8][i])
            row_as_list[8][i]-=accel_offset[i%3]

    
    altitude_list = []
    for pressure in row_as_list[5]:
        altitude_list.append(calculate_altitude(pressure))
    wind_speed = []
    wind_speed_at_90 = []
    wind_speed.append(hall_effect_sensor_to_wind_speed(row_as_list[11][0]))
    wind_speed_at_90.append(logarithmic_sheer(wind_speed[0],90))
    euler_angles = ahrs_algorithim(row_as_list[7], row_as_list[8]).tolist()
    lux_list = []
    for voltage in row_as_list[10]:
       if voltage != '': 
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
    final_converted_list[21] = row_as_list[17]
    final_converted_list[22] = row_as_list[18]
    final_converted_list[23] = row_as_list[19]
    final_converted_list[24] = row_as_list[20]
    final_converted_list[25] = row_as_list[21]
    final_converted_list[26] = altitude_list
    
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
            axis_labels = ["X","Y","Z"]
            p = 0
            for data in final_converted_list[i]:
               if data != '':   
                update_imu_table(final_converted_list_names[i] + axis_labels[p%3], float(data),final_converted_list[0][0],conn)
               p+=1
        if i > 9 and i < 17:
             for data in final_converted_list[i]:
               if data != '':    
                update_regular_table(final_converted_list_names[i], float(data), final_converted_list[0][0],conn)
        if i > 16 and i < 21:
            for data in final_converted_list[i]:
               if data != '':   
                update_gps_table(final_converted_list_names[i], float(data), final_converted_list[0][0],conn)
        if i > 20 and i < 26:
            for data in final_converted_list[i]:
               if data != '':   
                update_regular_table(final_converted_list_names[i], float(data), final_converted_list[0][0],conn)
        if i == 26:
            for data in final_converted_list[i]:
               if data != '':   
                update_regular_table(final_converted_list_names[i], float(data), final_converted_list[0][0],conn)

        if final_converted_list_names[i] in running_average_list:
            update_average_table(final_converted_list_names[i], final_converted_list[0][0], conn)
    last_ms = row_as_list[0][0]
    return 0

def is_malprinted_row_pre_check(row):
    has_all_brackets = false
    bracket_counter = 0
    for character in row:
        if '[' in character:
            bracket_counter+=1
        if ']' in character:
            bracket_counter+=1
    if bracket_counter == 20:
        has_all_brackets = true
    
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
    bat_tems = len(row_as_list[17]) + len(row_as_list[18])
    file_items = len(row_as_list[19]) + len(row_as_list[20])
    
    print(dht_items)
    print(bme_items)
    print(imu_items)
    print(gps_tems)
    print(bat_tems)
    print(file_items)
    
    
    if dht_items % 2 != 0 or bme_items % 4 != 0 or (imu_items - 1 ) % 9 != 0 or gps_tems % 7 !=0 or bat_tems % 2 !=0 or file_items % 2 != 0:
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
                try:
                    parse_file(readings_file)
                    print("Parsed")
                except KeyboardInterrupt:
                    print('Interrupted')
                    try:
                     sys.exit(130)
                    except SystemExit:
                     os._exit(130)
                except:
                    print("Failed To Parse")
            prev_time = t


  
