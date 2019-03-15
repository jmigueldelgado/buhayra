from os import listdir
import os
import shutil
import datetime
import sys
import logging
from buhayra.getpaths import *
import buhayra.utils as utils
import xml.etree.ElementTree
from snappy import Product
from snappy import GPF
from snappy import ProductIO
from snappy import jpy
from snappy import HashMap
from snappy import PixelPos
from snappy import GeoPos
from snappy import WKTReader
import json
import datetime
import subprocess
import re
import rasterio
import rasterio.mask
import fiona
from shutil import copyfile
from shapely.geometry import Polygon, shape
from shapely.ops import transform
import numpy as np
import time

System = jpy.get_type('java.lang.System')
BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')


def sar2sigma_subset(scenes):
    logger = logging.getLogger('root')
    time0=time.process_time()
    outForm='GeoTIFF+XML'
    finished=0
    with fiona.open(home['proj']+'/buhayra/auxdata/wm_utm_'+location['region']+'.gpkg','r') as wm:
        for f in scenes:
            logger.info("processing " + f)
            product = ProductIO.readProduct(sarIn+"/"+f)
            productName=product.getName()

            # if (productName+".finished") in listdir(sarIn):
            #     logger.info("product "+productName+" already processed: skipping")
            #     continue

            # logger.info("processing " + productName)
            rect_utm=getBoundingBoxScene(product)

            wm_in_scene,id_in_scene = getWMinScene(rect_utm,wm)

            # product=orbit_correction(product)
            product=remove_border_noise(product)
            product=thermal_noise_removal(product)
            product=calibration(product)
            product=speckle_filtering(product)
            product=geom_correction(product)
            product=set_no_data_value(product)

            logger.info("starting loop on reservoirs")
            targetdir = os.path.join(sarOut,productName)
            if not os.path.exists(targetdir):
                os.mkdir(targetdir)
            for i in range(0,len(id_in_scene)):
                fname=productName + "_" + str(id_in_scene[i])
                if (fname+".tif") in listdir(targetdir):
                    logger.debug("product "+fname+".tif already exists: skipping")
                    continue

                logger.debug("subsetting product "+ str(id_in_scene[i]))
                product_subset=subsetProduct(product,wm_in_scene[i])

                logger.debug("writing product "+ str(id_in_scene[i]))
                if os.path.exists(os.path.join(targetdir,fname + "_locked")):
                    os.remove(os.path.join(targetdir,fname + "_locked"))
                ProductIO.writeProduct(product_subset,os.path.join(targetdir,fname + "_locked"),outForm)
                product_subset.dispose()

                compress_tiff(os.path.join(targetdir,fname+'_locked.tif'),os.path.join(targetdir,fname+'.tif'))

            product.dispose()

            open(sarIn+"/"+productName + '.finished','w').close()
            finished=finished+1
            logger.info("**** " + f  + " processed in "+str((time.process_time()-time0)/60)+" minutes****")
            logger.info("**** processed " +str(finished)+" of "+ str(len(scenes))+" in loop ****")
    System.gc()
    logger.info("******************** finished loop: "+ str(len(scenes))+" scenes **")

def orbit_correction(product):
    logger = logging.getLogger('root')

    params = HashMap()
    root = xml.etree.ElementTree.parse(home['parameters']+'/orbit_correction.xml').getroot()
    for child in root:
        params.put(child.tag,child.text)

    result = GPF.createProduct('Apply-Orbit-File',params,product)
    logger.info("finished orbit correction")
    return(result)

def thermal_noise_removal(product):
    logger = logging.getLogger('root')

    params = HashMap()
    root = xml.etree.ElementTree.parse(home['parameters']+'/thermal_noise.xml').getroot()
    for child in root:
        params.put(child.tag,child.text)

    result = GPF.createProduct('ThermalNoiseRemoval',params,product)
    logger.info("finished ThermalNoiseRemoval")
    return(result)

### currently being performed with gpt
def thermal_noise_removal_gpt(product):
    logger = logging.getLogger('root')
    fname=product.getName()
    logger.info("writing product for thermal noise removal")
    ProductIO.writeProduct(product,sarIn+"/"+fname+'.dim',"BEAM-DIMAP")
    logger.info("finished writing. proceeding with gpt ThermalNoiseRemoval")
    product.dispose()

    subprocess.call(['/users/stud09/martinsd/local/snap/bin/gpt',
        'ThermalNoiseRemoval',
        '-SsourceProduct='+sarIn+'/'+fname+'.dim',
        '-PselectedPolarisations=VV',
        '-PremoveThermalNoise=true',
        '-t',
        sarIn+'/'+fname+'.dim'])

    result = ProductIO.readProduct(sarIn+"/"+fname + '.dim')
    logger.info("finished thermal noise removal")
    return(result)

def remove_border_noise(product):
    logger = logging.getLogger('root')

    params = HashMap()
    root = xml.etree.ElementTree.parse(home['parameters']+'/border-noise.xml').getroot()
    for child in root:
        params.put(child.tag,child.text)

    result = GPF.createProduct('Remove-GRD-Border-Noise',params,product)
    logger.info("finished Remove-GRD-Border-Noise")
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

def set_no_data_value(product):
    logger = logging.getLogger('root')
    params = HashMap()
    root = xml.etree.ElementTree.parse(home['parameters']+'/nodatavalue.xml').getroot()
    for child in root:
        params.put(child.tag,child.text)

    result = GPF.createProduct('SetNoDataValue',params,product)
    logger.info("finished set_no_data_value")
    return(result)

def sigma_naught(product):
    targetBands = jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor',1)
    targetBand1 = BandDescriptor()
    targetBand1.name = 'sigma_int'
    targetBand1.type = 'Int32'
    targetBand1.expression = 'round(log10(Sigma0_VV)*1000)'

    targetBands[0] = targetBand1

    parameters = HashMap()
    parameters.put('targetBands', targetBands)

    result = GPF.createProduct('BandMaths', parameters, product)
    return(result)

def subsetProduct(product,pol):
    # if pol.area<1000:
    buff=pol.buffer((pol.area)**0.5)
    # else:
        # buff=pol.buffer((pol.area)**0.5)

    bb=getBoundingBoxWM(buff)
    bb_ll=utils.utm2wgs(bb)
    geom = WKTReader().read(bb_ll.wkt)


    parameters = HashMap()
    parameters.put('copyMetadata', True)
    parameters.put('geoRegion', geom)
    product_subset = GPF.createProduct('Subset', parameters, product)
    return(product_subset)

def getWMinScene(rect,wm):
    wm_in_scene=list()
    id=list()
    for feat in wm:
        pol=geojson2shapely(feat['geometry'])
        pol=checknclean(pol)
        if rect.contains(pol):
            wm_in_scene.append(pol)
            id.append(feat['properties']['id'])
    return(wm_in_scene,id)

def getBoundingBoxScene(product):
    logger = logging.getLogger('root')
    gc=product.getSceneGeoCoding()
    rsize=product.getSceneRasterSize()
    h=rsize.getHeight()
    w=rsize.getWidth()

    p1=gc.getGeoPos(PixelPos(0,0),None)
    p2=gc.getGeoPos(PixelPos(0,h),None)
    p3=gc.getGeoPos(PixelPos(w,h),None)
    p4=gc.getGeoPos(PixelPos(w,0),None)

    rect=Polygon([(p1.getLon(),p1.getLat()),(p2.getLon(),p2.getLat()),(p3.getLon(),p3.getLat()),(p4.getLon(),p4.getLat())])
    rect_utm=utils.wgs2utm(rect)
    return(rect_utm)

def getBoundingBoxWM(pol):
    coords=pol.bounds
    bb=Polygon([(coords[0],coords[1]),(coords[0],coords[3]),(coords[2],coords[3]),(coords[2],coords[1])])
    return(bb)

def geojson2wkt(jsgeom):
    from shapely.geometry import shape,polygon
    polygon=shape(jsgeom)
    return(polygon.wkt)

def geojson2shapely(jsgeom):
    from shapely.geometry import shape,polygon
    polygon=shape(jsgeom)
    return(polygon)

def checknclean(pol):
    if not pol.is_valid:
        clean=pol.buffer(0)
        return(clean)
    else:
        return(pol)



def compress_tiff(inpath,outpath):
    with rasterio.open(inpath,'r') as ds:
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
        with rasterio.open(outpath,'w',driver=ds.driver,height=ds.height,width=ds.width,count=1,dtype=r_db.dtype) as dsout:
            dsout.write(r_db,1)
    with open(outpath[:-3]+'json', 'w') as fjson:
        json.dump(gdalParam, fjson)
    os.remove(inpath)
    os.remove(inpath[:-3]+'xml')
