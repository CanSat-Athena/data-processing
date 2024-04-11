from tkinter import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from matplotlib import pyplot as ply
import sqlite3 as sql
import numpy as np

root = Tk()
root.geometry("800x500")

graph_type_choice = IntVar()
graph_type_choice_label = Label(root, text= "You chose: ")
x_axis_data_choice_rt = StringVar()
x_axis_data_choice_rr = StringVar()
y_axis_data_choice_rr = StringVar()

x_axis_label = StringVar()
y_axis_label = StringVar()
graph_label = StringVar()

x_axis_label_entrybox = Entry(root, textvariable= x_axis_label)
x_axis_label_label = Label(root, text = "X - Axis Label")
y_axis_label_entrybox = Entry(root, textvariable= y_axis_label)
y_axis_label_label = Label(root, text = "Y - Axis Label")
graph_label_entrybox = Entry(root, textvariable= graph_label)
graph_label_label = Label(root, text = "Graph Label")




graph_data_choices = ["dhtTemp", "dhtHum", "bmeTemp", "bmeHum", "bmePres", "bmeGasRe", "imuAccel", "imuGyro", "imuMag", "eulerAngle", "ldrVoltage", "ldrLux", "ldrSolarIraddiance", "windTriggers", "windSpeed", "windSpeed90", "lat", "long", "alt", "fix", "batVolt", "batPerc", "fsUsa", "fsSize", "RSSI","alt_calc"]

imu_table_data = ["imuAccel", "imuGyro", "imuMag"]
regular_table_data = ["dhtTemp", "dhtHum", "bmeTemp", "bmeHum", "bmePres", "bmeGasRe", "eulerAngle", "ldrVoltage", "ldrLux", "ldrSolarIraddiance", "windTriggers", "windSpeed90", "batVolt", "batPerc", "fsUsa", "fsSize", "RSSI", "alt_calc"]
gps_table_data = ["lat", "long", "alt", "fix"]

x_axis_data_choice_rt_option = OptionMenu(root,  x_axis_data_choice_rt, *graph_data_choices)
x_axis_data_choice_rt_label = Label(root, text = "X - Axis Data")
x_axis_data_choice_rr_option = OptionMenu(root,  x_axis_data_choice_rr, *graph_data_choices)
x_axis_data_choice_rr_label = Label(root, text = "X - Axis Data")
y_axis_data_choice_rr_option = OptionMenu(root,  y_axis_data_choice_rr, *graph_data_choices)
y_axis_data_choice_rr_label = Label(root, text = "Y - Axis Data")


def make_reading_reading_graph(x_axis_data_name, y_axis_data_name, x_axis_label, y_axis_label, graph_label):
    x_axis_data = []
    x_axis_data_time = []
    y_axis_data = []
    
    db = sql.connect("cansatReadings.db")
    cur = db.cursor()
    
    if x_axis_data_name in imu_table_data:
        cur.execute("SELECT value FROM imuReadings where name = ?",(x_axis_data_name,))
        x_axis_data = cur.fetchall()
        cur.execute("SELECT timestamp FROM imuReadings where name = ?",(x_axis_data_name,))
        x_axis_data_time = cur.fetchall()
        for time in x_axis_data_time:
            cur.execute("SELECT value FROM imuReadings where name = ? AND timestamp = ?",(y_axis_data_name,time[0]))
            y_axis_data.append(cur.fetchone())
    elif x_axis_data_name in regular_table_data:
        print("Found")
        cur.execute("SELECT value FROM regularReadings where name = ?",(x_axis_data_name,))
        x_axis_data = cur.fetchall()
        cur.execute("SELECT timestamp FROM regularReadings where name = ?",(x_axis_data_name,))
        x_axis_data_time = cur.fetchall()
        for time in x_axis_data_time:
            cur.execute("SELECT value FROM regularReadings where name = ? AND timestamp = ?",(y_axis_data_name,time[0]))
            y_axis_data.append(cur.fetchone())
    elif x_axis_data_name in gps_table_data:
        cur.execute("SELECT value FROM gpsReadings where name = ?",(x_axis_data_name,))
        x_axis_data = cur.fetchall()
        cur.execute("SELECT timestamp FROM gpsReadings where name = ?",(x_axis_data_name,))
        x_axis_data_time = cur.fetchall()
        for time in x_axis_data_time:
            cur.execute("SELECT value FROM gpsReadings where name = ? AND timestamp = ?",(y_axis_data_name,time[0]))
            y_axis_data.append(cur.fetchone())
            
    print(x_axis_data)
    print(y_axis_data)        
    
    
    ply.scatter(x_axis_data,y_axis_data, s = 3)
    ply.xlabel(x_axis_label)
    ply.ylabel(y_axis_label)
    ply.title(graph_label)
    ply.savefig("graph.jpg")
    
    

def make_reading_time_graph(x_axis_data_name, x_axis_label, y_axis_label, graph_label):
    x_axis_data = []
    print(x_axis_data_name)
    time_data = []
    db = sql.connect("cansatReadings.db")
    cur = db.cursor()
    if x_axis_data_name in imu_table_data:
        cur.execute("SELECT value FROM imuReadings where name = ?",(x_axis_data_name,))
        x_axis_data = cur.fetchall()
        cur.execute("SELECT timestamp FROM imuReadings where name = ?",(x_axis_data_name,))
        time_data = cur.fetchall()
    elif x_axis_data_name in regular_table_data:
        print("Found")
        cur.execute("SELECT value FROM regularReadings where name = ?",(x_axis_data_name,))
        x_axis_data = cur.fetchall()
        cur.execute("SELECT timestamp FROM regularReadings where name = ?",(x_axis_data_name,))
        time_data = cur.fetchall()
    elif x_axis_data_name in gps_table_data:
        cur.execute("SELECT value FROM gpsReadings where name = ?",(x_axis_data_name,))
        x_axis_data = cur.fetchall()
        cur.execute("SELECT timestamp FROM gpsReadings where name = ?",(x_axis_data_name,))
        time_data = cur.fetchall()
    
   
    
    
    ply.plot(time_data,x_axis_data)
    ply.xlabel(x_axis_label)
    ply.ylabel(y_axis_label)
    ply.title(graph_label)
    ply.savefig("graph.jpg")
    


def make_graph():
    
    if graph_type_choice.get() == 1:
        make_reading_time_graph(x_axis_data_choice_rt.get(), x_axis_label.get(), y_axis_label.get(), graph_label.get())
    elif graph_type_choice.get() == 2:
        make_reading_reading_graph(x_axis_data_choice_rr.get(), y_axis_data_choice_rr.get(),x_axis_label.get(), y_axis_label.get(), graph_label.get())
    return 0


make_graph_button = Button(root, text = "Make Graph",command=make_graph )

def display_graph_choice_selection():
    
    graph_choice_button_one = Radiobutton(root, text = "Reading - Time", variable= graph_type_choice, value = 1)
    graph_choice_button_two = Radiobutton(root, text = "Reading - Reading", variable= graph_type_choice, value = 2)
    graph_choice_button_one.grid(column = 1, row = 1, padx = 10)
    graph_choice_button_two.grid(column = 1, row = 2, padx = 20)

def display_graph_choice_label():
    graph_choice_types = ["Reading - Time", "Reading - Reading"]
    graph_type_choice_label.configure(text = "You chose: " + graph_choice_types[int(graph_type_choice.get())-1])
    graph_type_choice_label.grid(column = 3, row = 3, pady = 20)

def display_rt_selection_boxes():
    x_axis_data_choice_rr_option.grid_remove()
    y_axis_data_choice_rr_option.grid_remove()
    x_axis_data_choice_rr_label.grid_remove()
    y_axis_data_choice_rr_label.grid_remove()
    
    x_axis_data_choice_rt_option.grid(column = 1, row = 5)
    x_axis_data_choice_rt_label.grid(column = 2, row = 5, padx = 20)

def display_rr_selection_boxes():
    x_axis_data_choice_rt_option.grid_remove()
    x_axis_data_choice_rt_label.grid_remove()
    #
    x_axis_data_choice_rr_option.grid(column = 1, row = 5)
    y_axis_data_choice_rr_option.grid(column = 1, row = 6)
    x_axis_data_choice_rr_label.grid(column = 2, row = 5, padx = 20)
    y_axis_data_choice_rr_label.grid(column = 2, row = 6, padx = 20)

def display_make_graph_button():
    make_graph_button.grid(column = 1, row = 12)

def display_axis_labelers():
    x_axis_label_entrybox.grid(column = 1, row = 8, pady = 10)
    y_axis_label_entrybox.grid(column = 1, row = 9, pady = 10)
    graph_label_entrybox.grid(column = 1, row = 10, pady = 10)
    
    x_axis_label_label.grid(column = 2, row = 8, pady = 10)
    y_axis_label_label.grid(column = 2, row = 9, pady = 10)
    graph_label_label.grid(column = 2, row = 10, pady = 10)

def display_data_selection_boxes():
    if graph_type_choice.get() == 1:
        display_rt_selection_boxes()
    elif graph_type_choice.get() == 2:
        display_rr_selection_boxes()
    display_axis_labelers()


display_graph_choice_selection()

while True:
    display_graph_choice_label()
    display_data_selection_boxes()
    display_make_graph_button()
    root.update()


