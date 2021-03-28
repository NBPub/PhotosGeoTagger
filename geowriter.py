# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 21:54:33 2021

@author: Nish
"""
# takes image and applies GPS data if possible
# overwrites file if data changes

from exif import Image
import numpy as np

def geowriter(path, lat, long, alt,checker, saveloc, name, errors):
    image = Image(path)
    try:
        image.gps_latitude = lat[0]
        image.gps_latitude_ref = lat[1]
        image.gps_longitude = long[0]
        image.gps_longtidue_ref = long[1]
    
        if np.isnan(alt) == False:
            if alt >= 0:
                image.gps_altitude = alt
            else:
                image.gps_altitude = 0
        
        with open(saveloc, 'wb') as new_image:
            new_image.write(image.get_file())
        
        return checker
        
    except Exception as e:
        checker = checker -1
        errors.loc[name, 'Message'] = e
        return checker
        pass