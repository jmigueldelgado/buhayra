import json
import geojson
from functools import partial
import shapely.geometry
import shapely.ops
import modules.getpaths as pths

def merge_pols(sceneMasks):
    mergedPolygon = shapely.geometry.Polygon()
    for fname in sceneMasks:
        with open(pths.s2aIn + '/' + fname) as geojson1:
            poly_geojson = json.load(geojson1)

            for feat in poly_geojson['features']:
                poly = shapely.geometry.asShape(feat['geometry'])
                mergedPolygon = mergedPolygon.union(poly)

    # using geojson module to convert from WKT back into GeoJSON format
    geojson_out = geojson.MultiPolygon(geometry=mergedPolygon)
    return(geojson_out)
