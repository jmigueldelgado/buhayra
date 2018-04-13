import zipfile
import subprocess
import os
import buhayra.getpaths as pths
import numpy as np
import re
from rasterio.warp import reproject,Resampling
from affine import Affine
import rasterio as rio
import json
import geojson
from functools import partial
import shapely.geometry
import shapely.ops

#pths.s2aIn="/home/delgado/Documents/tmp"
#sceneMasks = ['S2B_MSIL1C_20180225T125259_N0206_R052_T24MYV_20180225T131850.SAFE/GRANULE/L1C_T24MYV_A005083_20180225T125259/QI_DATA/MSK_CLOUDS_B00.geojson', 'S2B_MSIL1C_20180225T125259_N0206_R052_T24MYV_20180225T131850.SAFE/GRANULE/L1C_T24MYV_A005083_20180225T125259/QI_DATA/MSK_NODATA_B03.geojson', 'S2B_MSIL1C_20180225T125259_N0206_R052_T24MYV_20180225T131850.SAFE/GRANULE/L1C_T24MYV_A005083_20180225T125259/QI_DATA/MSK_NODATA_B08.geojson']

def list_pols(sceneMasks):
    listPolygon = list()
    for fname in sceneMasks:
#        fname=sceneMasks[0]
        print("opening masks:\n--- ",fname,"---\n")
        with open(pths.s2aIn + '/' + fname) as geojson1:
            poly_geojson = json.load(geojson1)

        for feat in poly_geojson['features']:
            listPolygon.append(feat['geometry'])
    return(listPolygon)

def merge_pols(sceneMasks):
    mergedPolygon = shapely.geometry.Polygon()
    for fname in sceneMasks:
#        fname=sceneMasks[0]
        with open(pths.s2aIn + '/' + fname) as geojson1:
            poly_geojson = json.load(geojson1)

        for feat in poly_geojson['features']:
            poly = shapely.geometry.asShape(feat['geometry'])
            mergedPolygon = mergedPolygon.union(poly)
    # using geojson module to convert from WKT back into GeoJSON format
    geojson_out = geojson.Feature(geometry=mergedPolygon,properties={})
    return(geojson_out)


def rmfmask():
    print("Executing rmclouds():")
    items=os.listdir(pths.s2aIn)
    for item in items:
        if re.search('^.*\.zip$', item) :
            print('unzipping' + item + '\n')
            item = pths.s2aIn + '/' + item
            sceneJp2 = unzipJp2(item)
            print('building vrt\n')
            runGdalbuildvrt(sceneJp2)
            print('fmask: making angles\n')
            runFmaskMakeAngles(sceneJp2)
            print('fmask: generating cloud mask\n')
            runFmaskStack(sceneJp2)
            print('fmask: finished ' + item+'\n')

#zipfl='/home/delgado/scratch/s2a_scenes/in.bak/S2B_MSIL1C_20180225T125259_N0206_R052_T24MYV_20180225T131850.zip'

def unzipJp2(zipfl):
    sceneZip = zipfile.ZipFile(zipfl)
    scenefls = sceneZip.namelist()
    sceneJp2=[]
    for line in scenefls:
        if re.search('.*IMG_DATA.*_B[0,3,8]{2}.*.jp2', line) :
            sceneJp2.append(line)
            if(not os.path.isfile(pths.s2aIn + '/' + line)):
                sceneZip.extract(line,pths.s2aIn)
    sceneZip.close()
    return(sceneJp2)


def unzipMasks(zipfl):
    sceneZip = zipfile.ZipFile(zipfl)
    scenefls = sceneZip.namelist()
    sceneMasks=[]
    for line in scenefls:
        if re.search('.*MSK_CLOUDS_B00.gml', line) :
            sceneZip.extract(line,pths.s2aIn)
            subprocess.check_call(['ogr2ogr','-f','GeoJSON',pths.s2aIn + '/' + line[:-3]+'geojson',pths.s2aIn + '/' + line])
            sceneMasks.append(line[:-3]+'geojson')
        if re.search('.*MSK_NODATA.*_B[0,3,8]{2}.*.gml', line) :
            sceneZip.extract(line,pths.s2aIn)
            subprocess.check_call(['ogr2ogr','-f','GeoJSON',pths.s2aIn + '/' + line[:-3]+'geojson',pths.s2aIn + '/' + line])
            sceneMasks.append(line[:-3]+'geojson')
    sceneZip.close()
    return(sceneMasks)

def getParentDir(path):
    parentdir=path.split('/')
    parentdir= parentdir[:-1]
    parentdir='/'.join(parentdir)
    return(parentdir)

def getBandPath(sceneJp2):
    bandpth=[]
    for jp2 in sceneJp2:
        bandpth.append(pths.s2aIn+ '/' + jp2)
    return(bandpth)

def getBandDir(sceneJp2):
    bandpth=getBandPath(sceneJp2)
    banddir=getParentDir(bandpth[0])
    return(banddir)

def getAngleDir(sceneJp2):
    banddir=getBandDir(sceneJp2)
    xmldir=getParentDir(banddir)
    return(xmldir)

def runGdalbuildvrt(sceneJp2):
    bandpth=getBandPath(sceneJp2)
    banddir=getBandDir(sceneJp2)

    cmd=[pths.gdalBuildvrt,
        "-resolution",
        "user",
        "-tr",
        "10",
        "10",
        "-separate",
        banddir + "/" + "allbands.vrt"] + bandpth
    cmd=" ".join(cmd)
    if not os.path.isfile(banddir + "/" + "allbands.vrt"):
        exitFlag=subprocess.call(cmd,shell=True)
    else:
        exitFlag="allbands.vrt already exists"
    return(exitFlag)

def runFmaskMakeAngles(sceneJp2):
    angledir=getAngleDir(sceneJp2)
    banddir=getBandDir(sceneJp2)
    cmd=[pths.fmaskMakeAngles,
        "-i",
        angledir + '/*.xml',
        "-o",
        banddir + '/angles.img']
    cmd=" ".join(cmd)
    if not os.path.isfile(banddir + '/angles.img'):
        exitFlag=subprocess.call(cmd,shell=True)
    else:
        exitFlag="angles.img already exists"
    return(exitFlag)

#fmask_sentinel2makeAnglesImage.py -i ../*.xml -o angles.img
#fmaskMakeAngles

def runFmaskStack(sceneJp2):
    banddir=getBandDir(sceneJp2)
    cmd = [pths.fmaskStack,
        "-a",
        banddir + "/allbands.vrt",
        "-z",
        banddir + "/angles.img",
        "-o",
        banddir + "/cloud.img"]
    cmd=" ".join(cmd)
    if not os.path.isfile(banddir + '/cloud.img'):
        exitFlag=subprocess.call(cmd,shell=True)
    else:
        exitFlag="cloud.img already exists"
    return(exitFlag)

#def filter_zeros(band):
#    band_out = band[band>0]
#    return(band_out)

def interpolate_clouds_to_10m(file_clouds):
    print('interpolate_clouds_to_10m:\n')
    print('Open files, reserve memory:\n')
    dataset_clouds = rio.open(file_clouds)
    clouds = dataset_clouds.read(1)
    clouds10 = np.empty(shape=(int(round(clouds.shape[0] * 2)),
        int(round(clouds.shape[1] * 2))))
    print('define transformation:\n')

    aff = dataset_clouds.transform
    newaff = Affine(aff[0] / 2, aff[1], aff[2],aff[3], aff[4] / 2, aff[5])
    print('Reproject: \n')
    reproject(clouds, clouds10,
        src_transform = aff,
        dst_transform = newaff,
        src_crs = dataset_clouds.crs,
        dst_crs = dataset_clouds.crs,
        resampling = Resampling.nearest)

    return(clouds10)
