#!/usr/bin/env python
# coding: utf-8

##########################################################################################
#### Import libraries
import requests
import os
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import pandas as pd
import glob
import numpy as np
import re
import shutil
import csv

substitutions = [
    # stuff to nuke
    ['<spacer.*?/spacer>', ' '],
    ['<chartHeader.*?/chartHeader>', ' '],

    # stuff to translate
    ['<CP_GEO_LOC.*?>', ''],
    ['</CP_GEO_LOC.*?>', ''],
    ['<CP_INDEX.*?>', '<span class="cp_index">'],
    ['</CP_INDEX.*?>', '</span>'],
    ['<CP_B.*?>', '<strong>'],
    ['</CP_B.*?>', '</strong>'],
    ['<CP_ITALIC.*?>', '<i>'],
    ['</CP_ITALIC.*?>', '</i>'],
    ['<cfr.*?>', ''],
    ['</cfr.*?>', ''],
    ['<table.*?>', ''],
    ['</table.*?>', ''],
    ['<image.*?>', ''],
    ['</image.*?>', ''],

    ['<paragraphHeader.*?>', '<div class="cp_paragraphHeader">'],
    ['</paragraphHeader.*?>', '</div>'],
    ['<paragraph.*?>', '<p class="cp_paragraph">'],
    ['</paragraph.*?>', '</p>'],
    ['<paraText.*?>', '<div class="cp_text">'],
    ['</paraText.*?>', '</div>'],
    ['<paraIndex.*?>', '<span class="cp_paraindex">'],
    ['</paraIndex.*?>', '</span>'],
]

##### All of the functions that will be needed for the script
# Return just the text portion of the paragraph
def plain_text_paragraph(paragraph):
    for sub in substitutions:
        paragraph = re.sub(sub[0], sub[1], paragraph, flags=re.IGNORECASE)
    print(paragraph)
    return paragraph


    # s1 = re.sub('<.*?>', '', paragraph)
    # s2 = re.sub("\t", '', s1)
    # s_out = re.sub(r"\(.*?\)", '', s2)
    # return(s_out)

# Return the Source IDs present in paragraphs
def return_geo_ids(paragraph):
    paragraph = paragraph.lower() # some of them are capitalized
    geo_ids = re.findall('<cp_geo_loc.*?</cp_geo_loc>', paragraph)
    geo_ids2 = [re.findall('source_id=\".*?\"', ids) for ids in geo_ids]
    geo_ids3 = [re.findall('\".*?\"', ids) for sublist in geo_ids2 for ids in sublist]
    geo_ids4 = [output for sublist in geo_ids3 for output in sublist]
    output_ids = [output[1:-1] for output in geo_ids4]
    return(output_ids)

# Make a dataframe from each entry
def entry_to_df(paragraph):
    sourceid_df = pd.DataFrame(return_geo_ids(paragraph), columns=['source_id'])
    sourceid_df['paragraph'] = plain_text_paragraph(paragraph)
    return(sourceid_df)

# See if the string is a digit or not
def test_num(x):
    if str(x).isdigit() == True:
        return(int(x))
    else:
        return(np.nan)

# Same, but testing to see if it's a name
def test_name(x):
    if str(x).isdigit() == True:
        return(np.nan)
    else:
        return(str(x))

# Make a list of files (There are 10 coast pilot publications)
url_list = list()

# for n in range(1,11):
for n in range(10,11):
    url_list.append('https://nauticalcharts.noaa.gov/publications/coast-pilot/files/cp' + str(n) + 
                    '/CPB' + str(n) + '_WEB.zip')

# Make blank data frames to export the ones from the loop
txt_master_df = []
loc_master_df = []
anchorage_master_df = []

redownload = False

##########################################################################################
# Big loop:
for url in url_list: # Loop through each URL
    coastpilot_number = url.split("/")[6] # Just the number of the publication
    print("Working on " + coastpilot_number)
    
    # Download the URL
    # Make a folder to put the unzipped data in
    output_zip_path = coastpilot_number + '.zip'
    output_folder = os.path.join("zip", coastpilot_number) 
    
    if(os.path.exists("zip") == False): # Make the "zip" folder if it doesn't exist
        os.mkdir("zip")
    if(os.path.exists(output_folder) == False): # Don't make it if it doesn't already exist
        os.mkdir(output_folder)
    
    if redownload:
        # Download the file
        #print("Requesting URL")
        rq = requests.get(url, allow_redirects=True)
        
        #print("Downloading URL")
        open(output_zip_path, 'wb').write(rq.content)
        
        # Unzip  the file
        #print("Unzipping")
        with ZipFile(output_zip_path, 'r') as zipObj:
            zipObj.extractall(output_folder)
        
        # To save space, delete the zipped file
        if os.path.exists(output_zip_path):
            os.remove(output_zip_path)
    
    # Get the names of all chapter files within this folder
    f_list = sorted(glob.glob(os.path.join(output_folder, "*_C*.xml")))




    #print("Parsing XML")
    # MAIN LOOP:
    # Loop through each chapter and pull the locations and text
    for file in f_list:
        chapter_short = file.split("_")[1] # Cut out the "CXX" part of the name (Chapter)
        #print("working on", chapter_short)
        
        # Open the chapter .xml
        doc_xml = ET.parse(file)
        
        root = doc_xml.getroot()
        
        # Get some values to give some information about the other fields
        chapter_title = ET.tostring(root, encoding='utf8').decode('utf8').split("chapterTitle>")[1].split("</")[0]
        booktitlenum = root.attrib["Number"]
        booktitle = root.attrib['Title']
        bookyear = root.attrib['Year']
        bookedition = root.attrib['Edition']
        bookchapternum = root.attrib['ChapterNo']
        
        ##### Step 1 -
        # First, get the location information
        # To do this, parse out the 'CP_GEO_LOC' and put them into a list
        output_list = list()
        for el in root.iter('CP_GEO_LOC'):
            output_list.append(el.attrib)
            
        # Since some of the attribute names are capitalized, 
        # we need to make them all lowercase in order to ensure compatability
        output_list_c = list()
        
        for entry in output_list:
            output_list_c.append({k.lower(): v for k, v in entry.items()})

        # Convert the list into a dataframe
        output_df = pd.DataFrame.from_dict(output_list_c)
        
        # Add some other fields to tell us where this came from, what edition, etc.
        output_df["chapter_title"] = chapter_title
        output_df["book_title"] = booktitle
        output_df["book_year"] = bookyear
        output_df["book_edition"] = bookedition
        output_df["book_chapter_number"] = bookchapternum
        
        # Append the df to the master
        if 'output_df' in locals(): # If it exists
            if output_df.shape[0] > 0: # If it has at least one row
                loc_master_df.append(output_df)
        
        ##### Step 2 -
        # Return the text information
        # First, turn the xml into a string, and separate it into a list
        all_text = ET.tostring(root, encoding='utf8').decode('utf8')
        all_text = all_text.split('\n')

        # Make a blank df to put the output into
        source_text_df = pd.DataFrame(columns=['source_id', 'paragraph'])
        for entry in all_text:
            entry_df = entry_to_df(entry)
            if(entry_df.shape[0] > 0):
                source_text_df = source_text_df.append(entry_df, ignore_index=True)

        # Append the df to the master
        if 'source_text_df' in locals(): # If it exists
            if source_text_df.shape[0] > 0: # If it has at least one row
                txt_master_df.append(source_text_df)
        
        ##### Step 3 -
        # Only return paragraphs with "anchorage" in them
        anchr_out = []
        for para in all_text:
            anchr = re.findall('nchorage', para.lower())
            if(len(anchr)) > 0:
                pt = plain_text_paragraph(para)
                if(len(pt)) > 11:
                    anchr_out.append(pt)
        anchr_df_out = pd.DataFrame({'text': anchr_out})
        anchr_df_out['book_num'] = booktitlenum
        anchr_df_out['chapter_num'] = bookchapternum
        
        # Append the df to the master
        if 'anchr_df_out' in locals(): # If it exists
            if anchr_df_out.shape[0] > 0: # If it has at least one row
                anchorage_master_df.append(anchr_df_out)
    
    if redownload:
        # When completed, remove the unzipped folder
        if(os.path.exists(output_folder) == True): 
            shutil.rmtree(output_folder)
            
        # On the last one, remove the 'zip' folder
        if url_list.index(url) == (len(url_list) - 1):
            shutil.rmtree('zip')


##########################################################################################
# Now that this is done, combine all of the df's in the location master
loc_master_df = pd.concat(loc_master_df, ignore_index=True)

# There is an error in the table which occasionally switches the county_name and county_numeric
# To fix it, make two columns and combine into one with the numeric values
c_num1 = loc_master_df["county_name"].apply(test_num)
c_num2 = loc_master_df["county_numeric"].apply(test_num)
num_out = c_num1.fillna(c_num2)

# Do the same thing with the county_name
c_name1 = loc_master_df["county_name"].apply(test_name)
c_name2 = loc_master_df["county_numeric"].apply(test_name)
name_out = c_name1.fillna(c_name2)

# Overwrite the values in the columns
loc_master_df["county_name"] = name_out
loc_master_df["county_numeric"] = num_out

# Drop duplicate source id's
loc_master_df = loc_master_df.drop_duplicates('source_id')

# Add a 'elev_in_ft' column
loc_master_df['elev_in_ft'] = loc_master_df.elev_in_m.apply(lambda x: pd.to_numeric(x) * 3.28084)

# If desired, export the df to a file
#loc_master_df.to_csv("loc_output_all.csv", index=False)

##########################################################################################
# Also combine the text master
txt_master_df = pd.concat(txt_master_df, ignore_index=True)

# There are some instances where the source_id is repeated with different paragraphs
# This will combine them into one paragraph
txt_master_df = txt_master_df.groupby('source_id')['paragraph'].apply(' '.join).reset_index()

# If desired, export the master_df to a file
#txt_master_df.to_csv("output_all_text.csv", index=False)

##########################################################################################
# Merge the two tables based on the source_id column
df_all = pd.merge(loc_master_df, txt_master_df, on='source_id', how='left')

# Fill in NA values
df_all = df_all.fillna(" ")

# If desired, write df_all to the working directory
#df_all.to_csv("df_all.csv", index=False)

##### Separate the tables into a mapbox output and a deepzoom output
# Mapbox output is just the lat/long and source ID



mapbox_output = df_all[['source_id', 'lat_dec', 'long_dec']]
mapbox_output.to_csv('_mapbox_output.csv',     
    quoting=csv.QUOTE_NONNUMERIC,
    escapechar="\\",
    doublequote=False, index=False)

# DeepZoom output has all other information, including the text paragraph
dz_output = df_all[['source_id', 'feature_name', 'feature_class', 'lat_dec', 'long_dec', 
                    'elev_in_m', 'elev_in_ft', 'paragraph']]
dz_output.to_csv('_deepzoom_database_output.csv', 
    quoting=csv.QUOTE_NONNUMERIC,
    escapechar="\\",
    doublequote=False, index=False)

##########################################################################################
# Combine all of the df's in the anchorage master
anchorage_master_df = pd.concat(anchorage_master_df, ignore_index=True)
anchorage_master_df.to_csv("_anchorages.csv",    
    quoting=csv.QUOTE_NONNUMERIC,
    escapechar="\\",
    doublequote=False, index=False)

