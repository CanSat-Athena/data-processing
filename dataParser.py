import csv
import sqlite3
from datetime import timezone, datetime    
import os


global_data_list = [[],[],[],[]]
previous_rows = []


def create_connection(data_text_file):
    connection = sqlite3.connect(data_text_file)
    return connection

def row_to_array():
    with open("readings.csv",'r') as csv_file:
        reader = csv.reader(csv_file)
        in_section = False
        section_counter = 0
        data_counter = 0
        current_row_number = 0
        for row in reader:
            if row not in previous_rows:
             in_section = False
             section_counter = 0
             data_counter = 0
             for data in row:
                value = data
                if '[' in data:
                    value = data[1:]
                    in_section = True
                    section_counter += 1
                if ']' in data:
                    value = data[:-1]
                    in_section = False
                    array_index = get_array_index(section_counter, data_counter)
                    global_data_list[array_index].append(value)
                if in_section:
                    array_index = get_array_index(section_counter, data_counter)
                    global_data_list[array_index].append(value)
                    data_counter +=1
            previous_rows.append(row)
    print(global_data_list)

def create_tables(connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS cansatReadings(dataType STRING, dataValue REAl, Timestamp REAL)''')
    connection.commit()
    
def parse_data(connection, row_number):
    section_counter = 0
    new_row_number = 0
    time_unix = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    data_names = ["latitiude", "longitude", "temp", "pressure"]
    cursor = connection.cursor()
    for section in global_data_list:
        for value in section:
            reading_name = data_names[section_counter]
            cursor.execute('''INSERT INTO cansatReadings(dataType, dataValue, Timestamp) VALUES(?,?,?)''',( reading_name,value,time_unix))
            connection.commit()
        section_counter+=1
    for section in global_data_list:
        section.clear()

def get_array_index(section_counter, data_counter):
    gps_data = [0,1]
    bme_data = [2]
    dht_data = [3]
    array_index = 0
    if section_counter == 1:
       array_index = gps_data[data_counter%2]
    elif section_counter == 2:
       array_index = bme_data[data_counter%1]
    elif section_counter == 3:
        array_index = dht_data[data_counter%1]
    return array_index


    
connection = create_connection("readings.db")
create_tables(connection)
   

get_time = lambda f: os.stat(f).st_ctime

fn = 'readings.csv'
prev_time = os.path.getmtime(fn)
row_number = 0

while True:
    
    t = os.path.getmtime(fn)
    if t != prev_time:
        row_to_array()
        parse_data(connection, row_number)
        
        print("Updated")
        prev_time = t