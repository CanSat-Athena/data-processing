from matplotlib import pyplot as plt
import numpy as np

measurementNames = ["Light" , "Humididty" , "Air Pressure" , "Wind" , "Temperature" , "VOC"]
measurementValues = [[1,2,3,4,5],[2,3,4,5,6],[3,4,5,6,7],[4,5,6,7,8],[5,6,7,8,9],[6,7,8,9,10]]

userXAxisChoice = input("What will be your X-Axis Measurement: ")
userYAxisChoice = input("What will be your Y-Axis Measurement: ")
xAxisChoiceIndex =measurementNames.index(userXAxisChoice)
yAxisChoiceIndex =measurementNames.index(userYAxisChoice)
plt.scatter(measurementValues[xAxisChoiceIndex],measurementValues[yAxisChoiceIndex])
plt.xlabel(userXAxisChoice)
plt.ylabel(userYAxisChoice)
plt.show()