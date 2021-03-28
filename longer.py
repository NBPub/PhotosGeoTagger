# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 21:54:32 2021

@author: Nish
"""

# take dd longitude and return DMS with W/E reference for Image EXIF data
# use return[0] to write to gps_longitude
# use return[1] to write to gps_longitude_ref

import numpy as np

def longer(x):
    if x < 0:
        long_ref = 'W'
        x = abs(x)
    else:
        long_ref = 'E'

    longD = np.floor(x)
    longMr = 60*(x - longD)
    longM = np.floor(longMr)
    longS = round(60*(longMr - longM),3)

    return (longD, longM, longS), long_ref