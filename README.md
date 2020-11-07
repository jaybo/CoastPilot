# CoastPilot
Coast Pilot processing

## Goal
Extract coordinates and related text information from each of the 14 chapters of the Coast Pilot XML documents (https://nauticalcharts.noaa.gov/publications/coast-pilot/index.html), reformat each item, and load it into a database.  Ultimately, https://www.deepzoom.com will display entries from this database. 

This should be a multistep process which can be rerun on demand.  A general flow chart is:

```
for each of the 14 source XML files:
    download the XML file from NOAA
    open the file
    for each entry in the XML file
        find the Latitude, Longitude locations and associated data (let's call this an 'entry')
        reformat each entry as necessary
        send each entry to a yet to be created Mapbox location database
    close the file
    optionally delete the file to save disk space
``` 
