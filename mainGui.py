from tkinter import *
import sqlite3 as sql
import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')
from tkintermapview import TkinterMapView
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 
import time
import os as os

get_time = lambda fn: os.path.getmtime(fn)

temp_values = [1,2,3,4,5]
press_values = [6,7,8,9,10]
alt_values = [11,12,13,14,15]
humid_values = [16,17,18,19,20]
wind_speed_values = [21,22,23,24,25]
light_intens_values = [26,27,28,29,30]
time_values = [0,0,0,0,0]

cansat_lat_long = [0,0]


false = False
true = True

has_landed = false
has_launched = false
has_deployed = false

alt_decrease_counter = 0
alt_same_counter = 0

root = Tk()

hasLandedLabel = Label(root, text = "Has Landed: " + str(has_landed))
hasDeployedLabel = Label(root, text = "Has Deployed: " + str(has_deployed))
hasLaunchedLabel = Label(root, text = "Has Launched: " + str(has_launched))

coordsLabel = Label(root, text= "")

root.geometry("600x400")


f = Figure(figsize=(3,2), dpi=100)
a = f.add_subplot(111)

canvas = FigureCanvasTkAgg(f, master=root)
canvas.draw()
canvas.get_tk_widget().grid(row=8, column=1, ipadx=40, ipady=20)


toolbarFrame = Frame(master=root)
toolbarFrame.grid(row=9,column=1)
toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)



def animate_alt_graph(i):
    
    x_axis_data=[]
    y_axis_data=[]
    
    db = sql.connect("cansatReadings.db")
    cur = db.cursor()
    cur.execute("SELECT value FROM regularReadings WHERE name = 'alt_calc'")
    y_axis_data = cur.fetchall()
    cur.execute("SELECT timestamp FROM regularReadings WHERE name = 'alt_calc'")
    x_axis_data = cur.fetchall()
    
    global a
    
    a.clear()
    a.scatter(x_axis_data,y_axis_data)

    
    
def checks_display():
    
    
    hasLandedLabel.grid(column= 2, row = 5)
    hasDeployedLabel.grid(column= 2, row = 6)
    hasLaunchedLabel.grid(column= 2, row = 7)
    
def update_checks():
    
  global has_launched
  global has_landed
  global has_deployed
  global alt_decrease_counter
  global alt_same_counter 
    
    
  if not has_launched:
    base_alt = -99
    current_alt = -100
    timestamp = 0
    db = sql.connect("cansatReadings.db")
    cur = db.cursor()
    
    cur.execute("SELECT value FROM baseLineReadings WHERE name = 'baseAltitude'")
    base_alt = cur.fetchone()
    if base_alt is not None:
        base_alt = float(base_alt[0])
    
    
        cur.execute("SELECT value FROM regularReadings WHERE name = 'alt'")
        current_alt = cur.fetchone()
        if current_alt is not None:
         current_alt = float(current_alt)
    
    
         cur.execute("SELECT timestamp FROM gpsReadings WHERE name = 'alt'")
         timestamp
         timestamp = cur.fetchone()
         if timestamp is not None:
          timestamp = float(timestamp[0])
    
         if base_alt != -99 and current_alt != -100:
            if (current_alt - 50) > base_alt:
             has_launched = true
             cur.execute("INSERT INTO flightChecks(name,hasHappened,timestamp) VALUES (?,?,?)", ("hasLaunched",true, timestamp))

    
  if not has_deployed and has_launched:
        previous_alts = []
        current_alt = 0
        current_fix = -1
        cur.execute("SELECT value FROM gpsReadings WHERE name = 'fix'")
        current_fix = cur.fetchone()
        if current_fix is not None:
            current_fix = int(current_fix)
        
            cur.execute("SELECT timestamp FROM gpsReadings WHERE name = 'alt'")  
            timestamp = 0
            timestamp = cur.fetchmany(30)
            if timestamp is not None:
             timestamp = float(timestamp[0])
        
            if current_fix != 0:
             cur.execute("SELECT value FROM gpsReadings WHERE name = 'alt'")
             previous_alts = cur.fetchall()
             current_alt = previous_alts[-1]
        else:
            cur.execute("SELECT value FROM regularReadings WHERE name = 'alt_calc'")
            previous_alts = cur.fetchmany(30)
            current_alt = previous_alts[-1]
        
            previous_alt_decrease_counter = 0
        
            if len(previous_alts) >= 30:
             for alt in previous_alts:
                alt = float(alt)
                current_alt = float(current_alt)
                if alt < current_alt:
                    previous_alt_decrease_counter+=1
                if previous_alt_decrease_counter == 3:
                    global alt_decrease_counter
                    alt_decrease_counter+=1
                    previous_alt_decrease_counter = 0
                if alt_decrease_counter >= 3:
                    has_deployed = true
                    cur.execute("INSERT INTO flightChecks(name,hasHappened,timestamp) VALUES (?,?,?)", ("hasDeployed",true, timestamp))
  if not has_landed and has_deployed:
      
        previous_alts = []
        current_alt = 0
        current_fix = -1
        cur.execute("SELECT value FROM gpsReadings WHERE name = 'fix'")
        current_fix = int(cur.fetchone())
        
        cur.execute("SELECT timestamp FROM gpsReadings WHERE name = 'alt'")
        timestamp = float(cur.fetchone())
        
        
        if current_fix != 0:
            cur.execute("SELECT value FROM gpsReadings WHERE name = 'alt'")
            previous_alts = cur.fetchmany(30)
            current_alt = previous_alts[-1]
        else:
            cur.execute("SELECT value FROM regularReadings WHERE name = 'alt_calc'")
            previous_alts = cur.fetchmany(30)
            current_alt = previous_alts[-1]

        previous_alt_close_counter = 0
        
        if len(previous_alts) >= 30:
            for alt in previous_alts:
                alt = float(alt)
                if abs(alt - current_alt) <= 10:
                    previous_alt_close_counter+=1
                if previous_alt_close_counter == 20:
                    alt_same_counter+=1
                    previous_alt_close_counter = 0
                if alt_same_counter == 3:
                    has_landed = true
                    cur.execute("INSERT INTO flightChecks(name,hasLanded,timestamp) VALUES (?,?,?)", ("hasDeployed",true, timestamp))

def display_table_titles():
    tempLabel = Label(root, text= "Temperature", borderwidth = 2, relief=  "solid")
    pressLabel = Label(root, text= "Pressure", borderwidth = 2, relief=  "solid")
    altLabel = Label(root, text= "Altitude", borderwidth = 2, relief=  "solid")
    humidLabel = Label(root, text= "Humidity",borderwidth = 2, relief=  "solid")
    windSpeedLabel = Label(root, text= "Wind Speed",  borderwidth= 2, relief=  "solid")
    lightIntensityLabel = Label(root, text= "Light Intensity", borderwidth= 2, relief=  "solid")
    timeLabel = Label(root, text= "Timestamp", borderwidth= 2, relief=  "solid")
    
    tempLabel.grid(row = 0, column = 1, padx= 20)
    pressLabel.grid(row = 0, column = 2, padx= 20)
    altLabel.grid(row = 0, column = 3, padx= 20)
    humidLabel.grid(row = 0, column = 4, padx= 20)
    windSpeedLabel.grid(row = 0, column = 5,)
    lightIntensityLabel.grid(row = 0, column = 6, padx= 20)
    timeLabel.grid(row = 0, column = 7, padx= 20)

def update_cansat_position():
        db = sql.connect("cansatReadings.db")
        cur = db.cursor()
        
        cur.execute('''SELECT value FROM gpsReadings WHERE name=?''',("lat",))
        last_lat_value = cur.fetchone()
        cur.execute('''SELECT value FROM regularReadings WHERE name=?''',("long",))
        last_long_value = cur.fetchone()
        
        if(last_lat_value != None):
            cansat_lat_long[0] =last_lat_value[0]
        if(last_long_value != None ):
            cansat_lat_long[1] = last_long_value[0]
        
        coordsLabel.config(text = "Lat: " + str(cansat_lat_long[0]) + " Long: " + str(cansat_lat_long[1]))
        coordsLabel.grid(column = 5, row = 6)

def ema_lists(data_list):
    print(data_list)
    adjusted_list = []
    if type(data_list[0]) is tuple:
        adjusted_list.append(data_list[0][0])
    else:
        adjusted_list.append(data_list[0])
    alpha = 0.7
    for i in range(1, len(data_list)):
        if type(adjusted_list[i-1]) is tuple:
            previous_adjust_value = adjusted_list[i-1][0]
        else:
            previous_adjust_value = adjusted_list[i-1]
        if type(data_list[i]) is tuple:
            adjusted_list.append((alpha * data_list[i][0]) + (1 - alpha)*(previous_adjust_value))
        else:
            adjusted_list.append((alpha * data_list[i]) + (1 - alpha)*(previous_adjust_value))
        
    return adjusted_list

def update_data_lists():
    db = sql.connect("cansatReadings.db")
    cur = db.cursor()
    all_temp_values = []
    all_press_values = []
    all_alt_values = []
    all_humid_values = []
    all_speed_values = []
    all_light_values = []
    all_time_values = []
    
    cur.execute('''SELECT value FROM regularReadings WHERE name=?''',("dhtTemp",))
    all_temp_values = cur.fetchall()
    cur.execute('''SELECT value FROM regularReadings WHERE name=?''',("bmePres",))
    all_press_values = cur.fetchall()
    cur.execute('''SELECT value FROM regularReadings WHERE name=?''',("dhtHum",))
    all_humid_values = cur.fetchall()
    cur.execute('''SELECT value FROM regularReadings WHERE name=?''',("windTriggers",))
    all_speed_values = cur.fetchall()
    cur.execute('''SELECT value FROM regularReadings WHERE name=?''',("ldrLux",))
    all_light_values = cur.fetchall()
    cur.execute('''SELECT value FROM regularReadings WHERE name=?''',("alt_calc",))
    all_alt_values = cur.fetchall()
    cur.execute('''SELECT timestamp FROM regularReadings WHERE name=?''',("ldrLux",))
    all_time_values = cur.fetchall()
    
    global temp_values
    global press_values
    global wind_speed_values
    global humid_values
    global alt_values   
    global light_intens_values
    
    for i in range(0,5):
        if len(all_temp_values) >= 5:
         temp_values[i] = all_temp_values[len(all_temp_values)-1-i]
    for i in range(0,5):
        if len(all_press_values) >= 5:
         press_values[i] = all_press_values[len(all_press_values)-1-i]
    for i in range(0,5):
        if len(all_alt_values) >= 5:
         alt_values[i] = all_alt_values[len(all_alt_values)-1-i]
    for i in range(0,5):
        if len(all_alt_values) >= 5:
         humid_values[i] = all_humid_values[len(all_humid_values)-1-i]
    for i in range(0,5):
        if len(all_speed_values) >= 5:
         wind_speed_values[i] = all_speed_values[len(all_speed_values)-1-i]
    for i in range(0,5):
        if len(all_light_values) >= 5:
         light_intens_values[i] = all_light_values[len(all_light_values)-1-i]
    for i in range(0,5):
        if len(all_time_values) >= 5:
         time_values[i] = all_time_values[len(all_time_values)-1-i]
         
         temp_values = ema_lists(temp_values)
         press_values = ema_lists(press_values)
         alt_values = ema_lists(alt_values)
         humid_values = ema_lists(humid_values)
         wind_speed_values = ema_lists(wind_speed_values)
         light_intens_values = ema_lists(light_intens_values)
         
         
         
         
    
         
def display_data_value():
    tempListBox = Listbox(root)
    pressListBox = Listbox(root)
    altListBox = Listbox(root)
    humidListBox = Listbox(root)
    windSpeedListBox = Listbox(root)
    lightIntensityListBox = Listbox(root)
    timeListBox = Listbox(root)    
    
    for i in range(0, len(temp_values)):
        tempListBox.insert(i,temp_values[i])
    for i in range(0, len(press_values)):
        pressListBox.insert(i,press_values[i])
    for i in range(0, len(alt_values)):
        altListBox.insert(i,alt_values[i])
    for i in range(0, len(humid_values)):
        humidListBox.insert(i,humid_values[i])
    for i in range(0, len(wind_speed_values)):
        windSpeedListBox.insert(i,wind_speed_values[i])
    for i in range(0, len(light_intens_values)):
        lightIntensityListBox.insert(i,light_intens_values[i])
    for i in range(0, len(time_values)):
        timeListBox.insert(i,time_values[i])
    
    tempListBox.grid(row = 1, column = 1, padx = 20)
    pressListBox.grid(row = 1, column = 2, padx = 20)
    altListBox.grid(row = 1, column = 3, padx = 20)
    humidListBox.grid(row = 1, column = 4, padx = 20)
    windSpeedListBox.grid(row = 1, column = 5, padx = 20)
    lightIntensityListBox.grid(row = 1, column = 6, padx = 20)
    timeListBox.grid(row = 1, column = 7, padx = 20)
    
ani_alt = animation.FuncAnimation(f, animate_alt_graph, interval=1000)    



fn = "cansatReadings.db"
t = 0
prev_time = t

while True:
    display_table_titles()
    display_data_value()
    t = get_time(fn)
    if t != prev_time:
      update_data_lists()
      update_cansat_position()
      update_checks()
      checks_display()
      prev_time = t
    root.update()