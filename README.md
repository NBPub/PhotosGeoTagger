# PhotosGeoTagger

Python functions to read Google location history and use the data to add GPS coordinates to viable photos. If an image's EXIF tag does not contain GPS data, the photo's date-taken information is used to find a match from one's location history.

Inspiration and start to code provided by: https://github.com/chuckleplant/blog/blob/master/scripts/location-geotag.py

## Usage
Use Google Takeout to obtain your location history. These functions use "Location History.json" and not the Semantic Location Histories. Note, this may be a big file.
https://takeout.google.com/settings/takeout

Run **locationtimetable.py** to convert your Google location history (*Location History.json*) takeout into a dataframe of times and GPS data. Then:

Run **beta.py** to run through a folder of photos, and add GPS data to viable images. . . OR

Run **betaFolder.py** to run through a directory of photo folders, and add GPS data to viable images.

If GPS data was added to an image, then the updated copy is saved to a "geocopies" folder, within the photofolder. Additionally a summary of the attempt(s) will be saved in the photofolder or the directory of photofolders.

## Disclaimer
While these functions should not edit the data on original photos (if data can be added, copies are saved), exercise caution and make backups of images to be processed.

If a photo does not have GPS data, and a match is found, then the coordinates will be added to the new copy, regardless of accuracy (see **Limitations**, below). Added location data should be reviewed before overwriting original images. If a photo has GPS data, then no attempt will be made to match or overwrite the existing data.
If there is demand for an overwrite function, I can add that to the repository.

## Limitations
The accuracy of location matching is reliant on the Google Location History data. If a photo is more than 24 hours away from the closest location match, it will be flagged as a "bad match". This threshold (1 day) could eventually be changed to a user-defined value. In the future, I may add an explorer function for Location History to investigate periods of no/low data and other fun stuff. For now you can check against something much fancier: https://www.google.com/maps/timeline

If photos to be processed were downloaded from Google Photos cloud storage, it may be possible to get metadata specific to each file during export. Using this export method and files would likely yield more accurate location matches.

#### Known Failure Modes
**Sea Level** Cannot add EXIF altitudes less than 0, so tagger will just leave negative values to be 0.

**\_gps\_IFD\_pointer** Cannot add EXIF GPS data without this in the EXIF tags. It specifies where in the tag to search for GPS data. Please reach out if you know of a way to properly set this parameter.

**Others?** Errors are saved when processing, so please share other error messages you may receive.


## Requirements
setup.py and requirements.txt generation in progress.

## Detailed Overview
Eventually create wiki

## Usecases
You have bunches of photos within your location history timespan that lack location data.

You have a camera that is not capable of adding GPS data to photos (some cameras can talk to your phone to add GPS data), and the timestamps are reasonably accurate.

## Links
https://www.google.com/maps/timeline

https://takeout.google.com/settings/takeout

https://chuckleplant.github.io/2018/07/23/google-photos-geotag.html
