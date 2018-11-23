import numpy as np
from os import listdir
import os
import shutil
import datetime
import sys
import logging
from buhayra.getpaths import *
import xml.etree.ElementTree
from snappy import Product
from snappy import GPF
from snappy import ProductIO
from snappy import jpy
from snappy import HashMap
from snappy import PixelPos
from snappy import GeoPos
from snappy import WKTReader
from shapely.geometry import Polygon
from shapely.ops import transform
import pyproj
from functools import partial
import fiona
import rasterio
import json
import datetime
import subprocess
import re

System = jpy.get_type('java.lang.System')
BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')


def sar2sigma(scenes):
    logger = logging.getLogger('root')

    outForm='GeoTIFF+XML'


    for f in scenes:
        logger.info("processing " + f)
        product = ProductIO.readProduct(sarIn+"/"+f)
        productName=product.getName()
        rect_utm=getBoundingBoxScene(product)
        wm_in_scene,id_in_scene = getWMinScene(rect_utm)


        if check_orbit(product.getName()):
            product_oc=orbit_correction(product)
        else:
            logger.info("skipping orbital correction for " + f+". Please download the relevant orbit files with `python buhayra get ``past scenes`` year month`")
            product_oc=product
        product_oc_tnr=thermal_noise_removal_gpt(product_oc)
        Cal=calibration(product_oc_tnr)
        # Cal=calibration(product)
        CalSf=speckle_filtering(Cal)
        CalSfCorr=geom_correction(CalSf)

        ProductIO.writeProduct(CalSfCorr,sarIn+"/"+fname,outForm)

        product.dispose()
        product_oc.dispose()
        product_oc_tnr.dispose()
        Cal.dispose()
        CalSf.dispose()
        CalSfCorr.dispose()
        ### remove scene from folder
        logger.info("REMOVING " + f)

        if os.path.isfile(sarIn+"/"+f):
            os.remove(sarIn+"/"+f)
        if os.path.isfile(sarIn+"/"+productName+'.dim'):
            os.remove(sarIn+"/"+productName+'.dim')
        if os.path.isdir(sarIn+"/"+productName+'.data'):
            shutil.rmtree(sarIn+"/"+productName+'.data')

        logger.info("**** sar2sigma completed!" + f  + " processed**********")
    System.gc()


        #
        # # GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
        # logger.info("starting loop on reservoirs")
        #  # i=0
        # for i in range(0,len(id_in_scene)):
        #
        #     fname=productName + "_" + str(id_in_scene[i]) + "_CalSfCorr"
        #     if (fname+".tif") in listdir(sarOut):
        #         logger.debug("product "+fname+".tif already exists: skipping")
        #         continue
        #
        #     logger.debug("subsetting product "+ str(id_in_scene[i]))
        #     product_subset=subsetProduct(CalSfCorr,wm_in_scene[i])
        #
        #     logger.debug("writing product "+ str(id_in_scene[i]))
        #     ProductIO.writeProduct(product_subset,sarOut+"/"+fname+'_big',outForm)
        #     product_subset.dispose()
        #     logger.info("Compressing and saving " + sarOut+"/"+fname+'_big'+'.tif')
        #     compress_tiff(sarOut+"/"+fname+'_big'+'.tif')
        #     path=sarOut+"/"+fname+'_big'+'.tif'



def select_last_scene():
    logger = logging.getLogger('root')
    if(len(listdir(sarIn))<1):
        logger.info(sarIn+" is empty! Nothing to do. Exiting and returning None.")
        f=None
    else:
        timestamp=list()
        scenes=list()
        for scn in listdir(sarIn):
            if re.search('.zip$',scn):
                scenes.append(scn)
                timestamp.append(datetime.datetime.strptime(scn.split('_')[4],'%Y%m%dT%H%M%S'))
        f=scenes[timestamp.index(max(timestamp))]
    return(f)

def select_past_scene(Y,M):
    logger = logging.getLogger('root')

    if(len(listdir(sarIn))<1):
        logger.info(sarIn+" is empty! Nothing to do. Exiting and returning None.")
        f=None
    else:
        timestamp=list()
        scenes_in_ym=list()
        for scn in listdir(sarIn):
            stamp=datetime.datetime.strptime(scn.split('_')[4],'%Y%m%dT%H%M%S')
            if re.search('.zip$',scn) and stamp.year==Y and stamp.month==M:
                scenes_in_ym.append(scn)
                timestamp.append(stamp)
        if(len(timestamp)<1):
            logger.info(sarIn+" has no scene for year "+Y+" and month "+M+"Exiting and returning None.")
            f=None
        else:
            f=scenes_in_ym[timestamp.index(max(timestamp))]
    return(f)

def select_scenes_year_month(Y,M):
    logger = logging.getLogger('root')

    if(len(listdir(sarIn))<1):
        logger.info(sarIn+" is empty! Nothing to do. Exiting and returning None.")
        scenes_in_ym=None
    else:
        timestamp=list()
        scenes_in_ym=list()
        for scn in listdir(sarIn):
            stamp=datetime.datetime.strptime(scn.split('_')[4],'%Y%m%dT%H%M%S')
            if re.search('.zip$',scn) and stamp.year==Y and stamp.month==M:
                scenes_in_ym.append(scn)
                timestamp.append(stamp)
        if(len(timestamp)<1):
            logger.info(sarIn+" has no scene for year "+Y+" and month "+M+"Exiting and returning None.")
            scenes_in_ym=None
    return(scenes_in_ym)

def geojson2wkt(jsgeom):
    from shapely.geometry import shape,polygon
    polygon=shape(jsgeom)
    return(polygon.wkt)

def geojson2shapely(jsgeom):
    from shapely.geometry import shape,polygon
    polygon=shape(jsgeom)
    return(polygon)



def getBoundingBoxScene(product):
    gc=product.getSceneGeoCoding()
    rsize=product.getSceneRasterSize()
    h=rsize.getHeight()
    w=rsize.getWidth()

    p1=gc.getGeoPos(PixelPos(0,0),None)
    p2=gc.getGeoPos(PixelPos(0,h),None)
    p3=gc.getGeoPos(PixelPos(w,h),None)
    p4=gc.getGeoPos(PixelPos(w,0),None)

    rect=Polygon([(p1.getLon(),p1.getLat()),(p2.getLon(),p2.getLat()),(p3.getLon(),p3.getLat()),(p4.getLon(),p4.getLat())])
    project = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'),
        pyproj.Proj(init='epsg:32724'))
    rect_utm=transform(project,rect)
    return(rect_utm)


def getBoundingBoxWM(pol):
    coords=pol.bounds
    bb=Polygon([(coords[0],coords[1]),(coords[0],coords[3]),(coords[2],coords[3]),(coords[2],coords[1])])
    return(bb)

def getWMinScene(rect):
    wm=fiona.open(home['home']+'/proj/buhayra/buhayra/auxdata/wm_utm_simplf.gpkg','r')
    wm_in_scene=list()
    id=list()
    for feat in wm:
        pol=geojson2shapely(feat['geometry'])
        pol=checknclean(pol)
        if rect.contains(pol):
            wm_in_scene.append(pol)
            id.append(feat['properties']['id'])
    wm.close()
    return(wm_in_scene,id)

def checknclean(pol):
    if not pol.is_valid:
        clean=pol.buffer(0)
        return(clean)
    else:
        return(pol)

def subsetProduct(product,pol):
    if pol.area<1000:
        buff=pol.buffer(10*(pol.area)**0.5)
    else:
        buff=pol.buffer((pol.area)**0.5)

    bb=getBoundingBoxWM(buff)
    project = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:32724'),
        pyproj.Proj(init='epsg:4326'))
    bb_ll=transform(project,bb)
    geom = WKTReader().read(bb_ll.wkt)


    parameters = HashMap()
    parameters.put('copyMetadata', True)
    parameters.put('geoRegion', geom)
    product_subset = GPF.createProduct('Subset', parameters, product)
    return(product_subset)


def check_orbit(fname):

    # check if orbit was downloaded
    startdt=datetime.datetime.strptime(fname.split('_')[4],'%Y%m%dT%H%M%S')
    stopdt=datetime.datetime.strptime(fname.split('_')[5],'%Y%m%dT%H%M%S')

    startdir=home['home']+\
                '/.snap/auxdata/Orbits/Sentinel-1/RESORB/'+fname[0:3]+'/'+\
                str(startdt.year)+\
                '/'+\
                str(startdt.month)+\
                '/'
    stopdir=home['home']+\
                '/.snap/auxdata/Orbits/Sentinel-1/RESORB/'+fname[0:3]+'/'+\
                str(stopdt.year)+\
                '/'+\
                str(stopdt.month)+\
                '/'

    orbits=list()
    if os.path.isdir(startdir):
        for orbit in os.listdir(startdir):
            orbits.append(orbit)

    if os.path.isdir(stopdir):
        for orbit in os.listdir(stopdir):
            orbits.append(orbit)
    check=False
    for orbit in orbits:
        orbit0=datetime.datetime.strptime(orbit.split('_')[6],'V%Y%m%dT%H%M%S')
        orbitf=datetime.datetime.strptime(orbit.split('_')[7],'%Y%m%dT%H%M%S.EOF')
        if ((orbit0<startdt) and (orbitf>stopdt)):
            check=True

    return check

def orbit_correction(product):
    logger = logging.getLogger('root')

    params = HashMap()
    root = xml.etree.ElementTree.parse(home['parameters']+'/orbit_correction.xml').getroot()
    for child in root:
        params.put(child.tag,child.text)

    result = GPF.createProduct('Apply-Orbit-File',params,product)
    logger.info("finished orbit correction")
    return(result)

### currently being performed with gpt
def thermal_noise_removal_gpt(product):
    logger = logging.getLogger('root')
    fname=product.getName()
    ProductIO.writeProduct(product,sarIn+"/"+fname+'.dim',"BEAM-DIMAP")
    product.dispose()

    subprocess.call(['/users/stud09/martinsd/local/snap/bin/gpt',
        'ThermalNoiseRemoval',
        '-SsourceProduct='+sarIn+'/'+fname+'.dim',
        '-PselectedPolarisations=VV',
        '-PremoveThermalNoise=true',
        '-t',
        sarIn+'/'+fname+'.dim'])

    result = ProductIO.readProduct(sarIn+"/"+fname + '.dim')
    logger.info("finished orbit correction")
    return(result)




def thermal_noise_removal(product):

    params = HashMap()
    root = xml.etree.ElementTree.parse(home['parameters']+'/thermal_noise.xml').getroot()
    for child in root:
        params.put(child.tag,child.text)

    result = GPF.createProduct('ThermalNoiseRemoval',params,product)
    return(result)




def calibration(product):
    logger = logging.getLogger('root')
    params = HashMap()
    root = xml.etree.ElementTree.parse(home['parameters']+'/calibration.xml').getroot()
    for child in root:
        params.put(child.tag,child.text)

    result = GPF.createProduct('Calibration',params,product)
    logger.info("finished calibration")
    return(result)

def speckle_filtering(product):
    ## Speckle filtering
    logger = logging.getLogger('root')

    params = HashMap()
    root = xml.etree.ElementTree.parse(home['parameters']+'/speckle_filtering.xml').getroot()
    for child in root:
        params.put(child.tag,child.text)

    result = GPF.createProduct('Speckle-Filter',params,product)
    logger.info("finished speckle filtering")
    return(result)

def geom_correction(product):
    ## Geometric correction
    logger = logging.getLogger('root')

    params = HashMap()
    root = xml.etree.ElementTree.parse(home['parameters']+'/terrain_correction.xml').getroot()
    for child in root:
        params.put(child.tag,child.text)

    result = GPF.createProduct('Terrain-Correction',params,product)
    # current_bands = CalSfCorr.getBandNames()
    # logger.debug("Current Bands after Terrain Correction:   %s" % (list(current_bands)))
    logger.info("finished geometric correction")
    return(result)


        # w=CalSfCorr.getSceneRasterWidth()
        # h=CalSfCorr.getSceneRasterHeight()
        # array = np.zeros((w,h),dtype=np.float32)  # Empty array
        # currentband=CalSfCorr.getBand('Sigma0_VV')
        # bandraster = currentband.readPixels(0, 0, w, h, array)

        # np.amax(bandraster)


def compress_tiff(path):
    with rasterio.open(path,'r') as ds:
        r=ds.read(1)
        r[r==0]=np.nan

        r_db=10*np.log10(r)*100

        if (np.nanmax(r_db)< np.iinfo(np.int16).max) and (np.nanmin(r_db) > (np.iinfo(np.int16).min+1)):
            r_db[np.isnan(r_db)]=np.iinfo(np.int16).min
            r_db=np.int16(r_db)
        else:
            r_db[np.isnan(r_db)]=np.iinfo(np.int32).min
            r_db=np.int32(r_db)

        gdalParam=ds.transform.to_gdal()
        with rasterio.open(path[:-8]+'.tif','w',driver=ds.driver,height=ds.height,width=ds.width,count=1,dtype=r_db.dtype) as dsout:
            dsout.write(r_db,1)

    with open(path[:-8]+'.json', 'w') as fjson:
        json.dump(gdalParam, fjson)
    os.remove(path)
    os.remove(path[:-3]+'xml')
