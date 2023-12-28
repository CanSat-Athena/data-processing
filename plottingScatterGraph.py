from matplotlib import pyplot as plt
import numpy as np

dataName = []
dataValue = []
dataTime = []

valuesFile = open("readingValues.txt", "r")


def parseData(valuefile):
    for line in valuefile:
        i = 1

        for word in line.split():
            if i == 1:
                dataName.append(word)
            if i == 2:
                dataValue.append(word)
            if i == 3:
                dataTime.append(word)
            i += 1


parseData(valuesFile)

for name in dataName:
    print(name)
for value in dataValue:
    print(value)
for time in dataTime:
    print(time)