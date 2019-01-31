import os
import fiona
from buhayra.getpaths import *
from shapely.geometry import mapping, Polygon, shape
import geojson
import buhayra.defAggregations as aggr

def getRandomSubset():

    bbox = Polygon([[-40.20,-3.0], [-38.3,-3.0], [-38.3,-4.50], [-40.20,-4.50]])
    path_to_geojson = aggr.ogr_getJRC()
    with fiona.open(path_to_geojson,'r') as latest:
        ids=list()

        for feat in latest:
            if not shape(feat['geometry']).within(bbox):
                continue
            ids.append({}.format(feat['properties']['id_jrc']))

    path_to_geojson = aggr.ogr_getRandomSubset(ids)
