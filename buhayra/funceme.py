import requests
import json
from buhayra.getpaths import *
import pymongo
from sshtunnel import SSHTunnelForwarder
import geojson


def get_reservoir_meta():
    res = requests.get('http://api.funceme.br/rest/acude/reservatorio', params={'paginator':False})
    pds=pandas.read_json(res.text)
    pds.to_csv(home['proj'] + '/buhayra/auxdata/reservoir_tbl.meta')

    with open(home['proj'] + '/buhayra/auxdata/reservoir.meta', 'w') as outfile:
        json.dump(res.json(), outfile)


def load_reservoir_meta():
    with open(home['proj'] + '/buhayra/auxdata/reservoir.meta') as json_data:
        res=json.load(json_data)
        json_data.close()
    return(res)

#def save_reservoir_meta_table():
#    res=load_reservoir_meta()
#    pandas.read_json(res.text)


def get_cav_api():
    res=load_reservoir_meta()
    for i in range(0,len(res):
        if res[i]['latitude']!=None
            cav = requests.get('http://api.funceme.br/v1/rest/acude/referencia-cav', params={'reservatorio.cod':res[i]['cod'],'paginator':False})

            feat_id = hav.insert_one(feat).inserted_id

            cav.json()
            #pdcav=pandas.read_json(cav.text,'columns')

#id=2481
#dt='2018-02-01'

def insert_insitu_monitoring(id_funceme,dt):
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
    insitu = db.insitu ##  collection
    toponyms = db.toponyms

    res=toponyms.find({'properties.id_funceme':id_funceme})
    if res is not empty and res['properties.cod'] != None:
        vol=requests.get('http://api.funceme.br/rest/acude/volume',params={'reservatorio.cod':id,'dataColeta.GTE':dt})

        for item in vol.json()['list']:
            record['date']=item['dataColeta']
            record['value']=item['valor']
            record['id_funceme']=id

            record_id = insitu.insert_one(record).inserted_id

    server.stop()
