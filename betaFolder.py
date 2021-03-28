# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 21:32:56 2021

@author: Nish
"""


import os
os.chdir(os.path.dirname(__file__))
from sys import exit

from latter import latter
from longer import longer
from geowriter import geowriter

import pandas as pd
import glob
import bisect
from exif import Image

print('\n')

# import location history data, see start for parsing json to dataframe to csv
print('Loading location data  . . .')
try:
    locations = pd.read_csv('locationdata.csv')
    locations = locations.drop(columns = 'Unnamed: 0') # dummy index
    locations.time = pd.to_datetime(locations.time) # convert back to datetime
    locstart = locations.time[0]
    locstop = locations.time[locations.shape[0]-1]
except:
    print()
    print('No location data available, run locationtimetable.py before continuing.')
    exit()

print('\n')
bigfolder = str(input('Enter directory of photos to try:  '))
print('\n')

folderlist = glob.glob(bigfolder + '/*')

summary = pd.DataFrame(index = [], columns = ['Total Images','# with GPS', 'Candidates', 'Added', 'Failed', 'No Date','Bad Matches', 'Beyond Location History'])
errors = pd.DataFrame(index = [], columns = ['Message'])
out_of_rangers = pd.DataFrame() 

print('Adding geo data  . . .')

for j, folder in enumerate(folderlist):
    print()
    photofolderlister = folder + '/*.jpg' # list of photos to try
    geofolder = folder + '\\geocopies\\'
    os.mkdir(geofolder)

    print('Working through', folder)

    # gather a directory of folders containing photos
    photolist = glob.glob(photofolderlister) 

    pics = pd.DataFrame(index = [], columns = ['t', 'gps', 'path', 'name', 'copyloc'])

    for i,val in enumerate(photolist):
        with open(val, 'rb') as image_file:
            picture = Image(image_file)
            pics.loc[i,'path'] = val
            pics.loc[i,'name'] = os.path.basename(val)
            pics.loc[i, 'copyloc'] = geofolder + os.path.basename(val)
            try:
                pics.loc[i,'t'] = picture.get('datetime')
                if picture.get('gps_latitude') == None:
                    pics.loc[i,'gps'] = 'n'
                else:
                    pics.loc[i,'gps'] = 'y'
            except:
                pics.loc[i,'t'] = None
                pics.loc[i,'path'] = val
                pics.loc[i,'gps'] = 'x'
                pass
                
            
    pics.t = pd.to_datetime(pics.t, format = '%Y:%m:%d %H:%M:%S')
    # check for pictures taken beyond the timespan of location history
    out_of_range = pics[(pics.t < locstart) | (pics.t > locstop)]
    pics = pics.drop(labels = out_of_range.index, axis = 0)
    pics = pics.reset_index(drop = True)

    del photolist
    del picture

    # if photo in directory does not have GPS data, then run functions to:
    # match time with location history
    # extract GPS coordinates from location history match
    # open file, input EXIF data, and save file

    checker = pics.shape[0]
    gotem = 0
    bad = 0
    notime = 0
    badmatch = pd.DataFrame(columns = ['Image', 'Offset', 'PicTime', 'LocTime'])

    for i,val in enumerate(pics.gps):
        if val == 'n':
            lindex = bisect.bisect_left(locations['time'],pics.loc[i,'t']) # find index on locations that closest matches picture's time
            offset = abs(locations['time'][lindex] - pics.t[i])
            latslice = locations.loc[lindex,'lat']*1e-7 # extract latitude, move decimal to correct location
            longslice = locations.loc[lindex,'long']*1e-7 # extract longitude
            imageloc = pics.loc[i,'path']
            saveloc = pics.loc[i,'copyloc']
            imagename = pics.loc[i,'name']
            
            # convert to format for writing EXIF tag
            gps_lat = latter(latslice) 
            gps_long = longer(longslice)
            gps_alt = locations.loc[lindex,'alt']
            
            # open image and write data
            checker = geowriter(imageloc, gps_lat, gps_long, gps_alt,checker, saveloc, imagename, errors)
            
            if offset > pd.to_timedelta('1 day'):
                badmatch.loc[bad,'Image'] = imagename
                badmatch.loc[bad,'Offset'] = offset.round('min')
                badmatch.loc[bad,'PicTime'] = pics.loc[i,'t']
                badmatch.loc[bad,'LocTime'] = locations['time'][lindex]
                bad = bad+1
            
        elif val == 'y':
             checker = checker-1
             gotem = gotem+1
        else:
            notime = notime + 1
            checker = checker - 1

    summary.loc[os.path.basename(folder), 'Total Images'] = pics.shape[0] + out_of_range.shape[0]
    summary.loc[os.path.basename(folder), '# with GPS'] = gotem
    summary.loc[os.path.basename(folder), 'Candidates'] = pics.shape[0] - gotem - notime
    summary.loc[os.path.basename(folder), 'Added'] = checker
    summary.loc[os.path.basename(folder), 'Failed'] = (pics.shape[0] - gotem - notime) - checker
    summary.loc[os.path.basename(folder), 'No Date'] = notime
    summary.loc[os.path.basename(folder), 'Bad Matches'] = bad
    summary.loc[os.path.basename(folder), 'Beyond location history'] = out_of_range.shape[0]
    
    if badmatch.shape[0] > 0:
        badmatch.to_csv(geofolder+ r'\badmatches.csv')
        
    if out_of_range.shape[0] > 0:
        out_of_rangers = out_of_rangers.append(out_of_range)
        
    newlist = len(glob.glob(geofolder + '/*'))
    if newlist == 0:
        os.rmdir(geofolder)



summary.to_csv(bigfolder + r'\summary.csv')
if errors.shape[0] > 0:
    errors.to_csv(bigfolder + r'\errors.csv')
    
if out_of_rangers.shape[0] > 0:
    out_of_rangers = out_of_rangers.drop(labels = ['copyloc', 'name'], axis = 1)
    out_of_rangers.to_csv(bigfolder + r'\out_of_range.csv')

print()        
print('All done.')

del bigfolder
del folderlist
del locations
