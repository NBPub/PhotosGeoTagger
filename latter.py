# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 21:54:30 2021

@author: Nish
"""

# take dd latitude and return DMS with N/S reference for Image EXIF data
# use return[0] to write to gps_latitude
# use return[1] to write to gps_latitude_ref

import numpy as np

def latter(x):
    if x < 0:
        lat_ref = 'S'
        x = abs(x)
    else:
        lat_ref = 'N'
        
    latD = np.floor(x)
    latMr = 60*(x - latD)
    latM = np.floor(latMr)
    latS = round(60*(latMr - latM),3)
    
    return (latD, latM, latS), lat_ref
    