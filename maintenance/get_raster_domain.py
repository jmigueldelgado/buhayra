import rasterio
from rasterio import features
import os
import numpy as np
from shapely.geometry import mapping, Polygon, shape
import json
import geojson

feats=list()

for f in os.listdir('/home/delgado/scratch_neb/dem'):
    if f.endswith('geoc_F.tif'):
        with rasterio.open(os.path.join('/home/delgado/scratch_neb/dem',f),'r') as ds:
            nparray = ds.read(1)
            nparray.fill(1)
            for pol, value in features.shapes(nparray, transform=ds.transform):
                if value==1:
                    feat = geojson.Feature(geometry=pol,properties={'file':f})
                    feats.append(feat)
                    
        # pol = shape(pol)
        # s = json.dumps(mapping(pol))
        # geom = json.loads(s)

featcoll=geojson.FeatureCollection(feats)
with open('/home/delgado/scratch_neb/dem/domain.geojson','w') as f:
    geojson.dump(featcoll,f)
