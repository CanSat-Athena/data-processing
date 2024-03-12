import csv
import sqlite3
from datetime import timezone, datetime    
import os


global_data_list = []
previous_rows = []


def create_connection(data_text_file):
    connection = sqlite3.connect(data_text_file)
    return connection

def row_to_array():
    with open("readings.csv",'r') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            inData = False
            element_counter = 0
            if row not in previous_rows: 
                print(row)
                for data in row:
                    value = data
                    if ':' in data:
                        inData = True
                        characterIndex = data.index(':') + 1
                        value = data[characterIndex:]
                    if inData:
                        print(element_counter)
                        print(value)
                        global_data_list.append(value)
                        element_counter+=1
                previous_rows.append(row)
            

def create_tables(connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS cansatReadings(dataType STRING, dataValue REAl, Timestamp REAL)''')
    connection.commit()
    
def parse_data(connection):
    time_unix = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    data_names = ["latitiude", "longitude","alt", "temp", "pressure"]
    cursor = connection.cursor()
    for value in global_data_list:
            reading_name = data_names[global_data_list.index(value)]
            cursor.execute('''INSERT INTO cansatReadings(dataType, dataValue, Timestamp) VALUES(?,?,?)''',( reading_name,value,time_unix))
            connection.commit()
            
    global_data_list.clear()

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
        parse_data(connection)
        
        print("Updated")
        prev_time = t