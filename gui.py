from tkinter import *
import sqlite3 as sql
import time
import os

root = Tk()
root.title("CanSat Readings")
root.geometry('400x400')

lblOne = Label(root,text = "Lat" )
lblTwo = Label(root,text = "Long" )
lblThree = Label(root,text = "Alt" )
lblFour = Label(root,text = "Temp" )
lblFive = Label(root,text = "Pressure" )
lblOne.grid(column = 1, row = 0)
lblTwo.grid(column = 3, row = 0)
lblThree.grid(column = 5, row = 0)
lblFour.grid(column = 7, row = 0)
lblFive.grid(column = 9, row = 0)

dataOne = Label(root,text = "0")
dataTwo = Label(root,text = "0")
dataThree = Label(root,text = "0")
dataFour = Label(root,text = "0")
dataFive = Label(root,text = "0")
dataOne.grid(column = 1, row = 2)
dataTwo.grid(column = 3, row = 2)
dataThree.grid(column = 5, row = 2)
dataFour.grid(column = 7, row = 2)
dataFive.grid(column = 9, row = 2)

def update_data():
    previous_latitudes = []
    previous_longitudes = []
    previous_altitudes = []
    previous_temps = []
    previous_pressures = []
    
    connection = sql.connect('readings.db')
    cursor = connection.cursor()
    
    cursor.execute('''SELECT dataValue FROM cansatReadings WHERE dataType = latitude''')
    previous_latitudes = cursor.fetchall()
    cursor.execute('''SELECT dataValue FROM cansatReadings WHERE dataType = longitude''')
    previous_longitudes = cursor.fetchall()
    cursor.execute('''SELECT dataValue FROM cansatReadings WHERE dataType = alt''')
    previous_altitudes = cursor.fetchall()
    cursor.execute('''SELECT dataValue FROM cansatReadings WHERE dataType = temp''')
    previous_temps = cursor.fetchall()
    cursor.execute('''SELECT dataValue FROM cansatReadings WHERE dataType = pressure''')
    previous_pressures = cursor.fetchall()
    
    dataOne.configure(text = previous_latitudes[-1])
    dataTwo.configure(text = previous_longitudes[-1])
    dataThree.configure(text = previous_altitudes[-1])
    dataFour.configure(text = previous_temps[-1])
    dataFive.configure(text = previous_pressures[-1])
    root.update()
    
    
get_time = lambda f: os.stat(f).st_ctime

fn = 'readings.db'
prev_time = os.path.getmtime(fn)


while True:
    root.update()
    t = os.path.getmtime(fn)
    if t != prev_time:
        update_data() 
        print("Updated")
        prev_time = t