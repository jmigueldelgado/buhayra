#! /usr/bin/env python3

import fiona as fio
from pygeotools.lib import geolib
from osgeo import ogr
import os
import sys
import rasterio as rio
import rasterio.mask
from statistics import mean
from collections import OrderedDict
import numpy.ma as ma
import numpy as np
import matplotlib.pyplot as plt
import pdb


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
        if len(poly) != 1: # special case for holes in polygons
            # create individual multiline geometry for each poly in multiploly
            lineGeom = ogr.Geometry(ogr.wkbLineString)
            # first list contains coordinates of embracing polygon
            for point in poly[0]:
                    lineGeom.AddPoint(point[0], point[1])
            outFeature = ogr.Feature(featureDefn)
            # Set new geometry
            outFeature.SetGeometry(lineGeom)
            # Add new feature to output Layer
            outLayer.CreateFeature(outFeature)
            # create points on line in sampling distance
            # IMPORTANT !!!
            # ogr.Geometry.AddPoint() adds height information
            # i.e a z coordinate which defaults to zero
            # in order to fix this issue, a 3rd dimension
            # needs to be added
            # to the function pygeotools.lib.geolib.line2pts
            # on line 947 and 948 for unpacking
            garbage, x, y = geolib.line2pts(lineGeom, sDist)
            sPtsX.extend(x)
            sPtsY.extend(y)
            # these polygons are the holes in the first polygon
            for hole in poly[1:]:
                lineGeom = ogr.Geometry(ogr.wkbLineString)
                for point in hole:
                    lineGeom.AddPoint(point[0], point[1])
                outFeature = ogr.Feature(featureDefn)
                outFeature.SetGeometry(lineGeom)
                outLayer.CreateFeature(outFeature)
                garbage, x, y = geolib.line2pts(lineGeom, sDist)
                sPtsX.extend(x)
                sPtsY.extend(y)

        else:  # simple polygon
            lineGeom = ogr.Geometry(ogr.wkbLineString)
            for line in poly:
                for point in line:
                    lineGeom.AddPoint(point[0], point[1])
            outFeature = ogr.Feature(featureDefn)
            outFeature.SetGeometry(lineGeom)
            outLayer.CreateFeature(outFeature)
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

# sample points
for key in sPoints:
    # Class rasterio._io.DatasetReaderBase implements method 'sample'
    # expects iterable with tuples of (x, y) and returns generator
    sPoints[key]['sampleVals'] = list(raster.sample(sPoints[key]['sampleCoords']))
    # convert list of 1d arrays to list of floats
    arrVals = []
    for arr in sPoints[key]['sampleVals']:
        arrVals.extend(arr.tolist())

    # remove values that were sampled outside of the raster
    arrVals = [i for i in arrVals if i > 0]
    # remove features that are outside valid raster bounds
    if not arrVals:
        sPoints.pop(key)
        break

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
            'latest_sample_MultiPoints.shp',
            fMode,
            crs=masks.crs,
            schema=mpSchema,
            driver="ESRI Shapefile") as c:
        c.write(samplingMP)

# mask raster and derive hav curve
hav = {}
for multipoly in masks.filter(bbox=raster.bounds):
    # out_image is ndarray
    out_image, out_transform = rasterio.mask.mask(raster,
                                             [multipoly['geometry']],
                                             crop=True,
                                             nodata=-9999)
    # write masked raster for inspection
    out_meta = raster.meta.copy()

    out_meta.update({"driver": "GTiff",
                 "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})

    id_cogerh = multipoly['properties']['id_cogerh']
    with rio.open("{}_masked.tif".
                  format(id_cogerh),
                  "w",
                  **out_meta) as dest:
        dest.write(out_image)

    # convert to masked array
    out_image = ma.masked_values(out_image, -9999.0)
    data = out_image[~out_image.mask]
    try:
        # get sample mean height
        mean_height = sPoints[str(id_cogerh)]['sampleMean']
        # create sequence of min height and mean height in reservoir
        height_seq = np.arange(data.min(), mean_height, 0.5).tolist()
        height_seq.append(mean_height)
    except KeyError:  # removed because outside valid raster bounds:149
        continue

    # use map with calculation function,
    # should be faster
    temp = []
    for h in height_seq:
        wl = h - data
        wl = ma.masked_less_equal(wl, 0)           # water level
        wa = pixelSizeX * pixelSizeY * wl.count()  # water area
        wv = pixelSizeX * pixelSizeY * wl.sum()    # water volume
        if wv is ma.masked:
            wv = 0
        temp.append([h, wa, wv])
    # hav[str(id_cogerh)] = temp

    # plot values and save
    x = [i[1] for i in temp]
    y = [i[2] for i in temp]
    plt.plot(x, y)
    plt.savefig('{}.png'.format(id_cogerh))
    plt.close()


