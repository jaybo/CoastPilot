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

# FSK: https://stackoverflow.com/questions/42981429/ssl-failure-on-windows-using-python-requests
# https://blog.devolutions.net/2020/07/tutorial-how-to-generate-secure-self-signed-server-and-client-certificates-with-openssl

import ssl
from requests.adapters import HTTPAdapter

auth = requests.auth.HTTPBasicAuth('averil', 'snort')
url = "https://localhost:44346/api/v1/markers/markersPublic"
#url = "https://deepzoom-test.azurewebsites.net/api/v1/data/markersPublic"


# class SSLContextAdapter(HTTPAdapter):
#     def init_poolmanager(self, *args, **kwargs):
#         context = ssl.create_default_context()
#         kwargs['ssl_context'] = context
#         context.load_default_certs() # this loads the OS defaults on Windows
#         return super(SSLContextAdapter, self).init_poolmanager(*args, **kwargs)

session = requests.Session()
# adapter = SSLContextAdapter()
# session.mount(url, adapter)

# print(requests.certs.where())

print(os.getcwd())

df = pd.read_csv(
    "D:/devGit/CoastPilot/_deepzoom_database_output.csv",
    escapechar="\\")

df.columns

features = ["Airport", "Arch", "Bar", "Bay", "Beach", "Bend", "Bridge", "Canal", "Cape", "Channel", "Cliff", "Crater", "Dam", "Flat", "Gap", "Gut", "Harbor", "Island", "Lake", "Lava", "Park", "Pillar",  "Populated Place", "Reservoir",  "River", "Stream", "Valley"]

# home = df[(df["lat_dec"] > 47) & (df["lat_dec"] < 48) & (df["long_dec"] < -122) & (df["long_dec"] > -123) & (df["feature_class"].isin(features)) ]
# print(home.head())
# print(len(home.index))

failures = 0

def upload(row):
    id = "GNIS" + str(row["source_id"])
    coordinates = [row["long_dec"], row["lat_dec"]]
    doc = row["paragraph"]
    is_anchorage = doc.find("nchor") > 0

    properties = {
        "isMarker": True,
        "access": "public",
        "name": row["feature_name"],
        "icon": "anchorage" if is_anchorage else "coastpilot" ,
        "id": id
    }

    marker = {
        "id": id,
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": coordinates,
        },
        "properties": properties
    }

    # TODO!! MAKE doc NULL AFTER INITIAL LOAD ELSE WIPE OUT EXISTING CONTENT!!!
    payload = {
        "id": id,
        "point": marker,
        "doc": "<p> </p>",      
        "coastPilot": doc
    }

    header = {"Content-type": "application/json"} 

    # response = session.post(url, data=payload, headers=header, auth=auth, cert=(cer, key))
    # response = requests.get("https://localhost:44346", verify=False)

    attempts = 10
    for attempt in range(attempts):
        try:
            response = session.post(url, data=json.dumps(payload), headers=header, auth=auth, verify=False)
            print (response.status_code, payload)
            if (response.status_code == 200):
                break
            print ("attempt: ", attempt)
            if (attempt == attempts - 1):
                failures += 1
        except:
            print ("error")
            failures += 1

count = 0
for index, row in df.iterrows():
    #print(row['paragraph'])
    upload(row)
    count += 1
    # if count > 10:
    #     break

print ("count: ", count, "failures: ", failures)