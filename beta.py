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
photofolder = str(input('Enter directory of photos to try:  '))
foldername = os.path.basename(photofolder)

photofolderlister = photofolder + '/*.jpg' # prep for glob
geofolder = photofolder + '\\geocopies\\' # folder for potential copies
os.mkdir(geofolder)

summary = pd.DataFrame(index = [], columns = ['Total Images','# with GPS', 'Candidates', 'Added', 'Failed', 
                                              'No Date','Bad Matches', 'Beyond location history'])
errors = pd.DataFrame(index = [], columns = ['Message'])

print()
print('Adding geo data  . . .')
print('\n')

# gather a particular directory of photos, check for GPS data
photolist = glob.glob(photofolderlister) # list of photos

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

out_of_range = pics[(pics.t < locstart) | (pics.t > locstop)]
out_of_range = out_of_range.drop(labels = ['copyloc', 'name'], axis = 1)
pics = pics.drop(labels = out_of_range.index, axis = 0)
pics = pics.reset_index(drop = True)

del photolist
del picture

# chop locations data into a smaller chunk, based on range of directory
start = pics.t.min()
stop = pics.t.max()
# use bisect to find index of closest value
start = bisect.bisect_left(locations['time'],start)
stop = bisect.bisect(locations['time'],stop)
# use bisect again, to expand range by one and not worry if start/stop is at bounds of locations
start = bisect.bisect_left(locations.index,start)
stop = bisect.bisect(locations.index,stop)

locations = locations.iloc[start:stop,:]
locations = locations.reset_index(drop = True)

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
        checker = geowriter(imageloc, gps_lat, gps_long, gps_alt,checker,saveloc, imagename, errors)
        
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

summary.loc[foldername, 'Total Images'] = pics.shape[0] + out_of_range.shape[0]
summary.loc[foldername, '# with GPS'] = gotem
summary.loc[foldername, 'Candidates'] = pics.shape[0] - gotem - notime
summary.loc[foldername, 'Added'] = checker
summary.loc[foldername, 'Failed'] = (pics.shape[0] - gotem - notime) - checker
summary.loc[foldername, 'No Date'] = notime
summary.loc[foldername, 'Bad Matches'] = bad
summary.loc[foldername, 'Beyond location history'] = out_of_range.shape[0]

newlist = len(glob.glob(geofolder + '/*.jpg'))
if newlist == 0:
    os.rmdir(geofolder)
    print('No new data added.')
else:
    summary.to_csv(geofolder+ r'\summary.csv')
    print(newlist, 'copies with geodata added, and summary table, saved to', geofolder)
    if badmatch.shape[0] > 0:
        print()
        print('Probable poor matches for', bad, 'images.')
        badmatch.to_csv(geofolder+ r'\badmatches.csv')
        print('CSV file saved to badmatches in geocopies folder.')
    if out_of_range.shape[0] > 0:
        print()
        out_of_range.to_csv(geofolder+ r'\out_of_range.csv')
        print('List of images outside time range also saved.')

print()        
print('All done.')

del pics
del photofolder
del locations
del checker
del geofolder
del badmatch
del summary
del out_of_range