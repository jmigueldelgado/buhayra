import numpy as np
from os import listdir
import os
import datetime
import sys
import numpy
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

System = jpy.get_type('java.lang.System')
BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')


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


def float2int(product):
    targetBands = jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor',1)
    targetBand1 = BandDescriptor()
    targetBand1.name = 'sigma_int'
    targetBand1.type = 'Int32'
    targetBand1.expression = 'round(Sigma0_VV*1000000)'

    targetBands[0] = targetBand1

    parameters = HashMap()
    parameters.put('targetBands', targetBands)

    result = GPF.createProduct('BandMaths', parameters, product)
    return(result)


def calibration(product):

    params = HashMap()
    root = xml.etree.ElementTree.parse(home['parameters']+'/calibration.xml').getroot()
    for child in root:
        params.put(child.tag,child.text)

    result = GPF.createProduct('Calibration',params,product)
    return(result)

def speckle_filtering(product):
    ## Speckle filtering

    params = HashMap()
    root = xml.etree.ElementTree.parse(home['parameters']+'/speckle_filtering.xml').getroot()
    for child in root:
        params.put(child.tag,child.text)

    result = GPF.createProduct('Speckle-Filter',params,product)
    return(result)

def geom_correction(product):
    ## Geometric correction

    params = HashMap()
    root = xml.etree.ElementTree.parse(home['parameters']+'/terrain_correction.xml').getroot()
    for child in root:
        params.put(child.tag,child.text)

    result = GPF.createProduct('Terrain-Correction',params,product)
    # current_bands = CalSfCorr.getBandNames()
    # logger.debug("Current Bands after Terrain Correction:   %s" % (list(current_bands)))
    return(result)


        # w=CalSfCorr.getSceneRasterWidth()
        # h=CalSfCorr.getSceneRasterHeight()
        # array = numpy.zeros((w,h),dtype=numpy.float32)  # Empty array
        # currentband=CalSfCorr.getBand('Sigma0_VV')
        # bandraster = currentband.readPixels(0, 0, w, h, array)

        # numpy.amax(bandraster)

def compressTiff(path):
    with rasterio.open(path,'r') as ds:
        r=ds.read(1)
        gdalParam=ds.transform.to_gdal()
        with rasterio.open(path[:-8]+'.tif','w',driver=ds.driver,height=ds.height,width=ds.width,count=1,dtype=r.dtype) as dsout:
            dsout.write(r,1)

    with open(path[:-8]+'.json', 'w') as fjson:
        json.dump(gdalParam, fjson)

    os.remove(path)
    os.remove(path[:-3]+'xml')

def sar2sigma():
    logger = logging.getLogger('root')


    logger.info("importing functions from snappy")

    outForm='GeoTIFF+XML'
    logger.debug(HashMap)
    logger.debug(BandDescriptor)
    logger.debug(System)

    f=selectScene()
    if f is None:
        logger.info("There are no scenes to process in "+sarIn+". Exiting")
        raise SystemExit()

    product = ProductIO.readProduct(sarIn+"/"+f)
    productName=product.getName()
    rect_utm=getBoundingBoxScene(product)
    wm_in_scene,id_in_scene = getWMinScene(rect_utm)

    logger.info("processing " + f)

    Cal=calibration(product)
    CalSf=speckle_filtering(Cal)
    CalSfCorr=geom_correction(CalSf)
    CalSfCorrInt=float2int(CalSfCorr)

    # current_bands = CalSfCorr.getBandNames()
    # logger.debug("Current Bands after converting to UInt8:   %s" % (list(current_bands)))

    # GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
    logger.info("starting loop on reservoirs")
    for i in range(0,len(id_in_scene)):

        fname=productName + "_" + str(id_in_scene[i]) + "_CalSfCorr"
        if (fname+".tif") in listdir(sarOut):
            logger.debug("product "+fname+".tif already exists: skipping")
            continue

        logger.debug("subsetting product "+ str(id_in_scene[i]))
        product_subset=subsetProduct(CalSfCorrInt,wm_in_scene[i])

        # # Get bandnames
        # im_bands = list(product_subset.getBandNames())
        #
        # # Get height and width
        # h = product_subset.getSceneRasterHeight()
        # w = product_subset.getSceneRasterWidth()
        # arr = np.zeros((h,w),dtype=np.float32)  # Empty array
        #
        # # Get the 1st band of the product for example
        # currentband = product_subset.getBand( im_bands[0])
        #
        # # Read the pixels from the band to the empty array
        # bandraster = currentband.readPixels(0, 0, w, h, arr)
        #
        # c=product_subset.getSceneGeoCoding()
        #
        # plt.imshow(bandraster)

        logger.debug("writing product "+ str(id_in_scene[i]))
        ProductIO.writeProduct(product_subset,sarOut+"/"+fname+'_big',outForm)
        product_subset.dispose()
        logger.info("Compressing and saving " + sarOut+"/"+fname+'_big'+'.tif')
        compressTiff(sarOut+"/"+fname+'_big'+'.tif')

    product.dispose()
    Cal.dispose()
    CalSf.dispose()
    CalSfCorr.dispose()
    CalSfCorrInt.dispose()
    System.gc()

    ### remove scene from folder
    logger.info("REMOVING " + f)

    os.remove(sarIn+"/"+f)


    logger.info("**** sar2watermask completed!" + f  + " processed**********")
