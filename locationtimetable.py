# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 14:58:59 2021

@author: Nish
"""

import pandas as pd
import json
import os
os.chdir(os.path.dirname(__file__))

locfolder = str(input('Enter directory containing location history JSON file:  '))


with open(locfolder + '\\Location History.json') as reader:
    data = json.load(reader)
    data = pd.DataFrame.from_dict(data['locations'])
del reader

data = data.drop(columns = ['accuracy', 'activity', 'verticalAccuracy', 'velocity', 'heading']) 
data.columns = ['time', 'lat', 'long', 'alt']
data['time'] = pd.to_datetime(data['time'], unit = 'ms', origin = 'unix')

print()
print('Location History.json read and saved to dataframe, locationdata.csv')
data.to_csv('locationdata.csv')

print()
locstart = data.time[0].round('min')
locstop = data.time[data.shape[0]-1].round('min')
noter = str(locstart) + ' to ' + str(locstop)

note = 'locationspan.txt'
with open(note, "w") as text_file:
    print(noter, file=text_file) # could use f string and go away from defining note


print('Location history spans from', noter)
print('File saved to note range, locationspan.txt')
