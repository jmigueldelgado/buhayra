import requests
import json
from buhayra.getpaths import *
from pymongo import MongoClient
from sshtunnel import SSHTunnelForwarder
import geojson
import datetime

def insert_toponyms():
    server = SSHTunnelForwarder(
        MONGO_HOST,
        ssh_username=username,
        ssh_password=password,
        remote_bind_address=('127.0.0.1', MONGO_PORT))

    server.start()

    client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port

    ## in case you want the local host:
    #client = MongoClient('mongodb://localhost:27017/')

    db = client.sar2watermask
    toponyms = db.toponyms

    with open(home['proj'] + '/buhayra/auxdata/res_meta.geojson') as geojson_data:
        topo=geojson.load(geojson_data)

    for item in topo['features']:
        topo_id = toponyms.update_one({'properties.cod':item['properties']['cod']},{'$set':item},upsert=True).upserted_id

    server.stop()

#        toponyms[0]['properties']['id_funceme']
#        toponyms[0]['properties']['cod']

def get_reservoir_meta():
    res = requests.get('http://api.funceme.br/rest/acude/reservatorio', params={'paginator':False})
    # pds=pandas.read_json(res.text)
    # pds.to_csv(home['proj'] + '/buhayra/auxdata/reservoir_tbl.meta')

    with open(home['proj'] + '/buhayra/auxdata/res_meta.geojson', 'w') as outfile:
        json.dump(res.json(), outfile)


def load_reservoir_meta():
    with open(home['proj'] + '/buhayra/auxdata/res_meta.geojson') as json_data:
        res=json.load(json_data)
        json_data.close()
    return(res)

#def save_reservoir_meta_table():
#    res=load_reservoir_meta()
#    pandas.read_json(res.text)


def api2hav():
    res=load_reservoir_meta()

    server = SSHTunnelForwarder(
        MONGO_HOST,
        ssh_username=username,
        ssh_password=password,
        remote_bind_address=('127.0.0.1', MONGO_PORT))

    server.start()

    client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port

    ## in case you want the local host:
    #client = MongoClient('mongodb://localhost:27017/')

    db = client.sar2watermask
    hav = db.hav

    for i in range(0,len(res)):
        if res[i]['latitude']!=None:
            cav = requests.get('http://api.funceme.br/v1/rest/acude/referencia-cav', params={'reservatorio.cod':res[i]['cod'],'paginator':False})
            for feat in cav.json():
                hav.update_one({'reservatorio':feat['reservatorio'],'codigo':feat['codigo']},{'$set':feat},upsert=True).upserted_id

    server.stop()

def insert_insitu_monitoring():
    #dt='2018-02-01'
    logger = logging.getLogger(__name__)
    dt=datetime.date.today()-datetime.timedelta(weeks=2)

    server = SSHTunnelForwarder(
        MONGO_HOST,
        ssh_username=username,
        ssh_password=password,
        remote_bind_address=('127.0.0.1', MONGO_PORT))

    server.start()
    logger.info("%s",server)

    client = MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port

    ## in case you want the local host:
    #client = MongoClient('mongodb://localhost:27017/')

    db = client.sar2watermask
    insitu = db.insitu ##  collection
    toponyms = db.toponyms
    logger.info("Connected to mongodb:")
    logger.info("%s",toponyms)

    topos=toponyms.find({'properties.id_funceme':{'$ne' : None}})
    logger.debug("%s",topos[0:5])

    for topo in topos:
        vol=requests.get('http://api.funceme.br/rest/acude/volume',params={'reservatorio.cod':topo['properties']['cod'],'dataColeta.GTE':dt})
        if len(vol.json()['list'])>0:
            for item in vol.json()['list']:
                vol.json()['list'][0]['dataColeta']
                item=vol.json()['list'][0]
                record={}
                record['date']=datetime.datetime.strptime(item['dataColeta'],"%Y-%m-%d %H:%M:%S")
                record['value']=item['valor']
                record['id_funceme']=topo['properties']['id_funceme']
                insert_id = insitu.update_one({'id_funceme':record['id_funceme'],'date':record['date']},{'$set':record},upsert=True).upserted_id
                logger.debug("%s",insert_id)
    server.stop()
