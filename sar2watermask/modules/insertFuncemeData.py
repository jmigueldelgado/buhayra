from defFuncemeApi import *
from getPaths import *
from pymongo import MongoClient
import json

if home['home']!='/home/riemer':
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
func = db.funceme ##  collection

reservs = getReservoir()

for reserv in reservs:
    code = reserv['properties']['code']
    ts = getRecentVolume(code)
    obj = ts[6:9]
    func.update({"reservoir":code},{"$addToSet" : {'timeSeries' : obj }},upsert=True) #### this is wrong


test=func.find({"reservoir":code})
