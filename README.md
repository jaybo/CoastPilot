# CoastPilot
Coast Pilot processing

## Goal
Extract coordinates and related text information from each of the 14 chapters of the Coast Pilot XML documents, reformat each item, and load it into a repository.  Ultimately, https://www.deepzoom.com will display this information. 

This should be a multistep process which can be rerun on demand.  A general flow chart is:

```
for each of the 14 source XML files:
    download the XML file from NOAA
    open the file
    for each entry in the XML file
        find the Latitude, Longitude locations and associated data (let's call this an 'entry')
        reformat each entry as necessary
        send each entry to a database
    close the file
    optionally delete the file to save disk space
``` 

## Tools

### VSCode
This is the most widely used code editor.  Install from:
https://code.visualstudio.com/docs/setup/setup-overview

### GitHub
Is the code storage repository.  You'll need to create an account with an email address.  There is a command line version of Git, or you can use GitHub for Windows (which I prefer):
https://desktop.github.com/

### Programming Language
I would advocate Python, but leave this up to you.  Other possible options are javascript and C#.
Install Python:  
https://www.python.org/downloads/
https://www.youtube.com/watch?v=RdD47NPku30  

## Do you have a laptop?

## Do you have a good email address?

## Contract
Here's how I'd anticipate this would work.  You'll probably spend a few weeks getting things set up, learning to use VSCode, and learning enough Python to be useful.  You don't get paid for that part.  But once you start on the actual work, you get paid at each milestone.

Commented code must be checked into this repository at each milestone.  

### Milestones

1. Completed script to download each of the 14 files to your local machine, then open and close each file.  $100.

2. Add to the above the ability to parse the XML and extract the Latitude, Longitude and details for each location. $100.

3. Reformat the data and send to a database.  I haven't actually figured out where the database will reside, so you'd be involved in helping to make this selection.  Possibilities are Azure Blobs, Mapbox, ...?  $300

4. Bonus.  Figure out how to make Mapbox search work with these entries.  $200

