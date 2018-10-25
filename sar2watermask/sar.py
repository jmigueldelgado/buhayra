from os import listdir
import datetime
import sys
import numpy
import logging
import json
from buhayra.getpaths import *



def sar2sigma(f):
    logger = logging.getLogger('root')


    import xml.etree.ElementTree
    from snappy import Product
    from snappy import GPF
    from snappy import ProductIO
    from snappy import jpy
    from snappy import HashMap


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
    wm_in_scene=getWMinScene(rect_utm)


    logger.info("processing " + f)

    logger.info("starting loop on reservoirs")

#### not yet necessary!    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

    pol=wm_in_scene[0]
    labelSubset=0

    for pol in wm_in_scene:
        product_subset=subsetProduct(product,pol)
        ### have to define labelSubset


        ## Calibration

        params = HashMap()

        root = xml.etree.ElementTree.parse(home['parameters']+'/calibration.xml').getroot()
        for child in root:
            params.put(child.tag,child.text)

        Cal = GPF.createProduct('Calibration',params,product_subset)

        ## Speckle filtering

        params = HashMap()
        root = xml.etree.ElementTree.parse(home['parameters']+'/speckle_filtering.xml').getroot()
        for child in root:
            params.put(child.tag,child.text)

        CalSf = GPF.createProduct('Speckle-Filter',params,Cal)

        ## Geometric correction

        params = HashMap()
        root = xml.etree.ElementTree.parse(home['parameters']+'/terrain_correction.xml').getroot()
        for child in root:
            params.put(child.tag,child.text)

        CalSfCorr = GPF.createProduct('Terrain-Correction',params,CalSf)

        current_bands = CalSfCorr.getBandNames()
        logger.debug("Current Bands after Terrain Correction:   %s" % (list(current_bands)))
        #GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
        ProductIO.writeProduct(CalSfCorr,sarOut+"/"+product.getName() + "_" + str(labelSubset) + "_CalSfCorr",outForm)

        ### release products from memory
        product_subset.dispose()
        Cal.dispose()
        CalSf.dispose()
        CalSfCorr.dispose()

    product.dispose()
    System.gc()

    ### remove scene from folder
    logger.info("REMOVING " + f)

    os.remove(sarIn+"/"+f)

    logger.info("**** sar2watermask completed!" + f  + " processed**********")



def selectScene():
    if(len(listdir(sarIn))<1):
        logger.info(sarIn+" is empty! Nothing to do. Exiting and returning None.")
        return None
    f=listdir(sarIn)[0]
    return(f)

def loadStaticWM():
    with open(home['home']+'/proj/buhayra/buhayra/auxdata/funceme.geojson') as fp:
        js = json.load(fp)
    return(js)

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
    import xml.etree.ElementTree
    from snappy import PixelPos
    from snappy import GeoPos
    from snappy import ProductIO
    from shapely.geometry import Polygon
    from shapely.ops import transform
    import pyproj
    from functools import partial

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
    from shapely.geometry import Polygon
    coords=pol.bounds
    bb=Polygon([(coords[0],coords[1]),(coords[0],coords[3]),(coords[2],coords[3]),(coords[2],coords[1])])
    return(bb)

def getWMinScene(rect):
    wm=loadStaticWM()
    wm_in_scene=list()
    id=list()
    for feat in wm['features']:
        pol=geojson2shapely(feat['geometry'])
        if rect.contains(pol):
            wm_in_scene.append(pol)
            id.append(feat['properties']['id'])
    return(wm_in_scene)

def subsetProduct(product,pol):
    from shapely.ops import transform
    import pyproj
    from functools import partial
    from snappy import jpy
    from snappy import GPF

    rect=getBoundingBoxScene(product)
    buff=pol.buffer(0.2*(pol.area)**0.5)
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
