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

cansat_lat_long = [51.371641808232035, -0.2339994106653362]


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



root.geometry("600x400")
map_widget = TkinterMapView(root, width= 300, height= 300)
map_widget.grid(column = 6, row = 10)
#cansat_marker = map_widget.set_position(cansat_lat_long[0], cansat_lat_long[1], marker= True)

f = Figure(figsize=(5,4), dpi=100)
a = f.add_subplot(111)

canvas = FigureCanvasTkAgg(f, master=root)
canvas.draw()
canvas.get_tk_widget().grid(row=1, column=0, ipadx=40, ipady=20)


toolbarFrame = Frame(master=root)
toolbarFrame.grid(row=2,column=0)
toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)

t = Figure(figsize=(5,4), dpi=100)
b = t.add_subplot(111)

canva = FigureCanvasTkAgg(t, master=root)
canva.draw()
canva.get_tk_widget().grid(row=2, column=0, ipadx=40, ipady=20)


toolbarFrames = Frame(master=root)
toolbarFrames.grid(row=3,column=0)
toolbas = NavigationToolbar2Tk(canvas, toolbarFrame)



    
    
    
    
    
    

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



def animate_imu_graph(i):
    
    x_axis_data=[]
    y_axis_data_x=[]
    y_axis_data_y=[]
    y_axis_data_x=[]
    
    db = sql.connect("cansatReadings.db")
    cur = db.cursor()
    cur.execute("SELECT value FROM imuReadings WHERE name = 'accelX'")
    y_axis_data_x = cur.fetchall()
    print(y_axis_data_x)
    cur.execute("SELECT value FROM imuReadings WHERE name = 'accelY'")
    y_axis_data_y = cur.fetchall()
    cur.execute("SELECT value FROM imuReadings WHERE name = 'accelZ'")
    y_axis_data_z = cur.fetchall()
    cur.execute("SELECT timestamp FROM imuReadings WHERE name = 'accelX'")
    x_axis_data = cur.fetchall()
    
    global b
    
    b.clear()
    b.scatter(x_axis_data,y_axis_data_x, color = "red" )
    b.scatter(x_axis_data,y_axis_data_y, color = "green" )
    b.scatter(x_axis_data,y_axis_data_z, color = "bluee" )
    
    
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
        base_alt = float(base_alt)
    
    
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
        
        last_lat_value = cansat_lat_long[0]
        last_long_value = cansat_lat_long[1]
        cur.execute('''SELECT value FROM gpsReadings WHERE name=?''',("lat",))
        last_lat_value = cur.fetchone()
        cur.execute('''SELECT value FROM regularReadings WHERE name=?''',("l",))
        last_long_value = cur.fetchone()
        
        if(last_lat_value != None):
            cansat_lat_long[0] =last_lat_value
        if(last_long_value != None ):
            cansat_lat_long[1] = last_long_value 
        
        print(cansat_lat_long)
     #  cansat_marker.set_position(cansat_lat_long[0][0], cansat_lat_long[1])
        time.sleep(1)
        root.update()

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
ani_imu = animation.FuncAnimation(t, animate_imu_graph, interval=1000) 


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
    root.update()