import json
import geojson
from bson import json_util
import os
import sys 
from datetime import datetime,timedelta,date
import requests

def getReservoir():
    url = 'http://api.funceme.br/rest/acude/reservatorio?paginator'
    
    r = requests.get(url)
    dams = json.loads(r.text)
    
    feats = []
    
    for dam in dams:
        pt = geojson.Point()
        pt['coordinates'] = [dam['longitude'],dam['latitude']]
        feats.append(geojson.Feature(geometry=pt,properties={ 'name':dam['nome'] , 'code' : dam['cod']}))

    feat_col = geojson.FeatureCollection(feats)
    return(feat_col)

def getRecentVolume(code):
    url = 'http://api.funceme.br/rest/acude/volume?reservatorio.cod=' + str(code) +'&dataColeta.GTE=' + str(date.today()-timedelta(days=33))
    r = requests.get(url)
    volumes = json.loads(r.text)
    ts = []
    for volume in volumes['list']:
        ts.append({'timestamp' : datetime.strptime(volume['dataColeta'],"%Y-%m-%d %H:%M:%S"), 'value' : volume['valor'] })
    return(ts)
    
