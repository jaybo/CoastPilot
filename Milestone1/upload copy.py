# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

# %%
#!/usr/bin/env python
# coding: utf-8

##########################################################################################
#### Import libraries
import requests
import json
import os
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import pandas as pd
import glob
import numpy as np
import re
import shutil
import csv

print(os.getcwd())

df = pd.read_csv(
    "D:/devGit/CoastPilot/_deepzoom_database_output.csv",
    escapechar="\\")

df.columns

features = ["Bay", "Canal", "Cape", "Channel", "River", "Stream"]

home = df[(df["lat_dec"] > 46) & (df["lat_dec"] < 48) & (df["long_dec"] < -121) & (df["long_dec"] > -124) & (df["feature_class"].isin(features)) ]

print(home.head())

print(len(home.index))

auth = requests.auth.HTTPBasicAuth('arnie', 'snarf')
url = "https://localhost:44346/api/v1/data/markersPublic"
#url = "https://deepzoom-test.azurewebsites.net/api/v1/data/markersPublic"
cer = "D:/devGit/CoastPilot/mypem.pem"
key = "D:/devGit/CoastPilot/mykey.key"

def upload(row):
    id = "GNIS" + str(row["source_id"])
    coordinates = [row["long_dec"], row["lat_dec"]]
    properties = {
        "isMarker": True,
        "access": "public",
        "name": row["feature_name"],
        "icon": "coastpilot",
        "id": id
    }
    doc = row["paragraph"]

    marker = {
        "id": id,
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": coordinates,
        },
        "properties": properties
    }
    payload = {
        "id": id,
        "point": marker,
        "doc": doc,
    }

    header = {"Content-type": "application/json"} 

    response = requests.post(url, data=payload, headers=header, auth=auth, cert=(cer, key))
    print (response.status_code, payload)
    # response_json = response_decoded_json.json()

for index, row in home.iterrows():
    #print(row['paragraph'])
    upload(row)
    if index > 3:
        break

