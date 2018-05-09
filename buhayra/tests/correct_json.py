from pymongo import MongoClient
import geojson
import os
import sys
from datetime import datetime
from buhayra.getpaths import *
from sshtunnel import SSHTunnelForwarder
import numpy as np

if socket.gethostname()!='ubuntuserver':
    server = SSHTunnelForwarder(
        MONGO_HOST,
        ssh_username=MONGO_USER,
        ssh_password=MONGO_PASS,
        remote_bind_address=('127.0.0.1', MONGO_PORT))

    server.start()
    print("started ssh tunnel")

    client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port
else:
    print("connecting to local host")
    client = MongoClient('mongodb://localhost:27017/')


db = client.sar2watermask
s2w = db.sar2watermask ##  collection

f = open(home['home'] + '/correct_json.log','w')
id=25028
ids=s2w.distinct("properties.id_cogerh")
for id in ids[0:100]:
    feats=s2w.find({"properties.id_cogerh":id})
    feats[0]
    for feat in feats:
        if feat["geometry"]["type"]=='Polygon' and str(feat["geometry"]["coordinates"])[0:3]!='[[[' and str(feat["geometry"]["coordinates"])[0:2]=='[[':
            feat["geometry"]["coordinates"]=[feat["geometry"]["coordinates"]]
            f.write("Corrected one Polygon with id_cogerh: " + str(feat["properties"]["id_cogerh"]) +"\n" )
            f.write("The start of the coordinate string looks like: " + str(feat["geometry"]["coordinates"])[0:6] +"\n" )

        if feat["geometry"]["type"]=='MultiPolygon' and str(feat["geometry"]["coordinates"])[0:4]!='[[[[' and str(feat["geometry"]["coordinates"])[0:3]=='[[[':
            feat["geometry"]["coordinates"]=[feat["geometry"]["coordinates"]]
            f.write("Corrected one MultiPolygon with id_cogerh: " + str(feat["properties"]["id_cogerh"])  +"\n")
            f.write("The start of the coordinate string looks like: " + str(feat["geometry"]["coordinates"])[0:6] +"\n" )


#    s2w.find_one_and_update({"_id" : feat["_id"]},{ "$set" : {"geometry.coordinates" : feat["geometry"]["coordinates"]}})
f.close()



if home['hostname']!='ubuntuserver':
    server.stop()
