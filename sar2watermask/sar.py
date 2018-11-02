from os import listdir
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
from shapely.geometry import Polygon
from shapely.ops import transform
import pyproj
from functools import partial
import fiona



def selectScene():
    if(len(listdir(sarIn))<1):
        logger.info(sarIn+" is empty! Nothing to do. Exiting and returning None.")
        return None
    f=listdir(sarIn)[0]
    return(f)

#jsgeom=js['features'][0]['geometry']

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
    WKTReader = jpy.get_type('com.vividsolutions.jts.io.WKTReader')
    geom = WKTReader().read(bb_ll.wkt)

    HashMap = jpy.get_type('java.util.HashMap')
    #GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

    parameters = HashMap()
    parameters.put('copyMetadata', True)
    parameters.put('geoRegion', geom)
    product_subset = GPF.createProduct('Subset', parameters, product)
    return(product_subset)


def float2int(product):
    BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')

    targetBand1 = BandDescriptor()
    targetBand1.name = 'sigma_int'
    targetBand1.type = 'Int32'
    targetBand1.expression = 'round(Sigma0_VV*1000000)'

    targetBands = jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor',1)
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




def sar2sigma():
    logger = logging.getLogger('root')


    logger.info("importing functions from snappy")

    outForm='GeoTIFF+XML'
    HashMap = jpy.get_type('java.util.HashMap')
    System = jpy.get_type('java.lang.System')
    BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')
    logger.debug(HashMap)
    logger.debug(BandDescriptor)
    logger.debug(System)


    f=selectScene()
    product = ProductIO.readProduct(sarIn+"/"+f)
    rect_utm=getBoundingBoxScene(product)
    wm_in_scene,id_in_scene = getWMinScene(rect_utm)

    logger.info("processing " + f)

    Cal=calibration(product)
    CalSf=speckle_filtering(Cal)
    CalSfCorr=geom_correction(CalSf)
    CalSfCorrInt=float2int(CalSfCorr)

    # current_bands = CalSfCorr.getBandNames()
    # logger.debug("Current Bands after converting to UInt8:   %s" % (list(current_bands)))


    logger.info("starting loop on reservoirs")
#### not yet necessary!    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
    # for i in range(0,len(id_in_scene)):
    for i in range(2000,2004):
        product_subset=subsetProduct(CalSfCorrInt,wm_in_scene[i])
        labelSubset = id_in_scene[i]

        #GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
        ProductIO.writeProduct(product_subset,sarOut+"/"+product.getName() + "_" + str(labelSubset) + "_CalSfCorr",outForm)

        # w=product_subset.getSceneRasterWidth()
        # h=product_subset.getSceneRasterHeight()
        # array = numpy.zeros((w,h),dtype=numpy.int32)  # Empty array
        # currentband=product_subset.getBand('sigma_int')
        # bandraster = currentband.readPixels(0, 0, w, h, array)
        # numpy.amax(bandraster)

        ### release products from memory
        product_subset.dispose()

    product.dispose()
    Cal.dispose()
    CalSf.dispose()
    CalSfCorr.dispose()
    CalSfCorrInt.dispose()
    System.gc()

    ### remove scene from folder
    logger.info("REMOVING " + f)

    #os.remove(sarIn+"/"+f)

    logger.info("**** sar2watermask completed!" + f  + " processed**********")
