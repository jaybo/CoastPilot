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

# FSK: https://stackoverflow.com/questions/42981429/ssl-failure-on-windows-using-python-requests
# https://blog.devolutions.net/2020/07/tutorial-how-to-generate-secure-self-signed-server-and-client-certificates-with-openssl

import ssl
from requests.adapters import HTTPAdapter

auth = requests.auth.HTTPBasicAuth('arnie', 'snarf')
url = "https://localhost:44346/api/v1/data/markersPublic"
#url = "https://deepzoom-test.azurewebsites.net/api/v1/data/markersPublic"
cer = "D:/devGit/CoastPilot/client1.crt"
csr = "D:/devGit/CoastPilot/client1.csr"
key = "D:/devGit/CoastPilot/client1.key"



class SSLContextAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        kwargs['ssl_context'] = context
        context.load_default_certs() # this loads the OS defaults on Windows
        return super(SSLContextAdapter, self).init_poolmanager(*args, **kwargs)

session = requests.Session()
# adapter = SSLContextAdapter()
# session.mount(url, adapter)

print(requests.certs.where())

print(os.getcwd())

df = pd.read_csv(
    "D:/devGit/CoastPilot/_deepzoom_database_output.csv",
    escapechar="\\")

df.columns

features = ["Bay", "Canal", "Cape", "Channel", "River", "Stream"]

home = df[(df["lat_dec"] > 46) & (df["lat_dec"] < 48) & (df["long_dec"] < -121) & (df["long_dec"] > -124) & (df["feature_class"].isin(features)) ]

print(home.head())

print(len(home.index))



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

    # response = session.post(url, data=payload, headers=header, auth=auth, cert=(cer, key))
    response = requests.get("https://localhost:44346", verify=False)

    response = requests.post(url, body=payload, headers=header, auth=auth, verify=False)
    print (response.status_code, payload)
    # response_json = response_decoded_json.json()

for index, row in home.iterrows():
    #print(row['paragraph'])
    upload(row)
    if index > 3:
        break

