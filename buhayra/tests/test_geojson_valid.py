from pymongo import MongoClient
import geojson
import os
import sys
from datetime import datetime
from buhayra.getpaths import *
from sshtunnel import SSHTunnelForwarder

server = SSHTunnelForwarder(
    MONGO_HOST,
    ssh_username=MONGO_USER,
    ssh_password=MONGO_PASS,
    remote_bind_address=('127.0.0.1', MONGO_PORT))

server.start()

client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port

## in case you want the local host:
#client = MongoClient('mongodb://localhost:27017/')

db = client.sar2watermask
s2w = db.sar2watermask ##  collection


newlist = []
items=os.listdir("/home/delgado/Documents")
items
for names in items:
    if names.endswith('simplified.geojson'):
        newlist.append(names)
newlist[1]

with open("/home/delgado/Documents" + '/' + newlist[1]) as f:
    data = json.load(f)

feat=data["features"][2]
feat["geometry"].is_valid
feat["geometry"]["coordinates"]


for feat in data["features"]:
    dttm = datetime.strptime(feat["properties"]["ingestion_time"],"%Y/%m/%d %H:%M:%S+00")
    feat["properties"]["ingestion_time"] = dttm
    feat["properties"]["source_id"] = int(feat["properties"]["source_id"])
    #dicio = {"geometry":feat["geometry"],"id_cogerh":feat["properties"]["id_cogerh"]}
    #feat_id = s2w.update_one(feat,{"$set" : feat},upsert=True).upserted_id
    feat_id = s2w.insert_one(feat).inserted_id

feat_id
feat["geometry"]["coordinates"]
