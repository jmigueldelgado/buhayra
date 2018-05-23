#! /usr/bin/env python3

############################
# TODO
# x convert multipolygon features to polygon features (or iterate each polygon feature)
# x convert polygon features to lines
# x create evenly spaced (in raster resolution or less) points between points of line
# x sample points in raster and calc mean
# 5 mask raster with multipolygon
# 6 further steps see original tdx2hav script from Shuping
############################

import fiona as fio
from pygeotools.lib import geolib
from osgeo import ogr
import os
import sys
import rasterio as rio
from statistics import mean
from collections import OrderedDict
import pdb


def map2pixel(x, y, geotransform):
    """Converts geospatial coordinates to pixel (array) coordinates

    Parameters
    ----------
    x : int, float
        x coordinate
    y : int, float
        y coordinate
    geotransform : list or tuple of int, float
        GDAL transform in its native form

    Returns
    ----------
    (x, y): tuple of int
        Pixel coordinates
    """
    ulX = geotransform[0]
    ulY = geotransform[3]
    xDist = geotransform[1]
    yDist = geotransform[5]
    col = int((x - ulX) / xDist)
    row = int((ulY - y) / -yDist)
    return (col, row)


pathIn = os.path.expanduser("~/Seafile/UniArbeit/hykli/aktuell/pythonHavData/in")
pathOut = os.path.expanduser("~/Seafile/UniArbeit/hykli/aktuell/pythonHavData/out")

os.chdir(pathIn)

rasterF = "dfd2_506519819_sum_dem_20151214_5x5_geoc_F.tif"
raster = rio.open(rasterF)

vectorF = "latest.geojson"
masks = fio.open(vectorF)

os.chdir(pathOut)

# check if crs is the same
if raster.crs != masks.crs:
    print('Datasets are in different coordinate reference systems \n'
          'Please reproject them first\n'
          'Stopped')
    sys.exit()

# get raster resolution (for sampling)
pixelSizeX, pixelSizeY = raster.res
# sampling distance (half the raster resolution)
sDist = (pixelSizeX + pixelSizeY) / 4

# empty dict to hold all sampling points (lists)
sPoints = {}
# only process features intersecting the raster
# create points for sampling
for multipoly in masks.filter(bbox=raster.bounds):
    # save geometry from further processing for inspection
    outDriver = ogr.GetDriverByName('GeoJSON')
    sourceName = (('{}_test.geojson')
        .format(str(multipoly['properties']['id_cogerh'])))
    outDataSource = outDriver.CreateDataSource(sourceName)
    outSRS = ogr.osr.SpatialReference()
    outSRS.ImportFromEPSG(32724)
    outLayer = outDataSource.CreateLayer(
        sourceName,
        outSRS,
        geom_type=ogr.wkbLineString)
    featureDefn = outLayer.GetLayerDefn()
    # empty lists to hold sampling points for one multipolygon
    sPtsX = []
    sPtsY = []
    # check if multipolygon is empty
    isEmpty = 1 if len(multipoly['geometry']['coordinates']) == 0 else 0
    if isEmpty:
        print('GeoJSON feature with oid {} contains empty geometry ... skipping'
              .format(multipoly['properties']['oid']))
        continue
    # get each individual polygon in multipolygon
    for poly in multipoly['geometry']['coordinates']:
        # create individual multiline geometry for each poly in multiploly
        lineGeom = ogr.Geometry(ogr.wkbLineString)
        # get each line in polygon
        for line in poly:
            for point in line:
                lineGeom.AddPoint(point[0], point[1])
        # rest of feature creation for inspection
        # create a new feature
        outFeature = ogr.Feature(featureDefn)
            # Set new geometry
        outFeature.SetGeometry(lineGeom)
        # Add new feature to output Layer
        outLayer.CreateFeature(outFeature)
        # create points on line in sampling distance
        # IMPORTANT !!!
        # ogr.Geometry.AddPoint() adds height information
        # i.e a z coordinate which defaults to zero
        # in order to fix this issue, a 3rd dimension needs to be added
        # to the function pygeotools.lib.geolib.line2pts
        # on line 947 and 948 for unpacking
        garbage, x, y = geolib.line2pts(lineGeom, sDist)
        sPtsX.extend(x)
        sPtsY.extend(y)

    # dereference the feature
    outFeature = None
    # Save and close DataSources
    outDataSource = None

    # add list to dictionary with id_cogerh as key
    key = str(multipoly['properties']['id_cogerh'])
    sPoints[key] = {'sampleCoords': list(zip(sPtsX, sPtsY))}

# multipoint schema
mpSchema = {'geometry': 'MultiPoint',
    'properties': OrderedDict([
        ('id_cogerh', 'int'),
        ('meanElev',  'float')
        #('rasterElev','float')
    ])
}

for key in sPoints:
    # sample points
    # Class rasterio._io.DatasetReaderBase implements method 'sample'
    # expects iterable with tuples of (x, y) and returns generator
    sPoints[key]['sampleVals'] = list(raster.sample(sPoints[key]['sampleCoords']))
    # convert list of 1d arrays to list of floats
    arrVals = []
    for arr in sPoints[key]['sampleVals']:
        arrVals.extend(arr.tolist())
    # set values in dict
    sPoints[key]['sampleVals'] = arrVals
    # compute mean
    sPoints[key]['sampleMean'] = mean(sPoints[key]['sampleVals'])

    # create geojson file to inspect results
    samplingMP = {
        'geometry': {
            'type': 'MultiPoint',
            'coordinates':
                (sPoints[key]['sampleCoords'])
        },
        'properties': OrderedDict([
            ('id_cogerh', key),
            ('meanElev', sPoints[key]['sampleMean'])
            #('rasterElev', sPoints[key]['sampleVals'])
        ])
    }

    if os.path.isfile('latest_sample_MultiPoints.shp'):
        fMode = 'a'
    else:
        fMode = 'w'
    with fio.open(
            'latest_sample_MultiPoints.shp', fMode,
            crs=masks.crs,
            schema=mpSchema,
            driver="ESRI Shapefile") as c:
        c.write(samplingMP)
