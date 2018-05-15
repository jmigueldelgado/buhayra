import requests
import json
from buhayra.getpaths import *
import pymongo
import pandas

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


def get_water_level(id,dt):
    id=2481
    dt='2018-02-01'
    requests.get('http://api.funceme.br/rest/acude/volume',params={'reservatorio.cod':id,'dataColeta.GTE':dt})
    http://api.funceme.br/rest/acude/volume?reservatorio.cod=2481&dataColeta.GTE=2018-02-01
