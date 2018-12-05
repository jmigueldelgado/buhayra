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
import json
import datetime
import subprocess
import re
import rasterio
import rasterio.mask
import fiona
from shutil import copyfile
from shapely.geometry import Polygon, shape
import pyproj
from functools import partial
from shapely.ops import transform
import numpy as np
import dask.distributed

System = jpy.get_type('java.lang.System')
BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')


def sar2sigma(scenes):
    logger = logging.getLogger('root')

    outForm='GeoTIFF+XML'
    with fiona.open(home['home']+'/proj/buhayra/buhayra/auxdata/wm_utm_simplf.gpkg','r') as wm:
        for f in scenes:
            logger.info("processing " + f)
            product = ProductIO.readProduct(sarIn+"/"+f)
            productName=product.getName()

            logger.info("processing " + productName)
            rect_utm=getBoundingBoxScene(product)

            wm_in_scene,id_in_scene = getWMinScene(rect_utm,wm)

            product=orbit_correction(product)
            product=remove_border_noise(product)
            product=thermal_noise_removal(product)
            product=calibration(product)
            product=speckle_filtering(product)
            product=geom_correction(product)
            product=set_no_data_value(product)
#            product=sigma_naught(product)

            logger.info("starting loop on reservoirs")
            for i in range(0,len(id_in_scene)):
                fname=productName + "_" + str(id_in_scene[i])
                if (fname+".tif") in listdir(sarOut):
                    logger.debug("product "+fname+".tif already exists: skipping")
                    continue

                logger.debug("subsetting product "+ str(id_in_scene[i]))
                product_subset=subsetProduct(product,wm_in_scene[i])

                logger.debug("writing product "+ str(id_in_scene[i]))
                ProductIO.writeProduct(product_subset,sarOut+"/locked",outForm)
                product_subset.dispose()

                compress_tiff(sarOut+'/locked.tif',sarOut+'/'+fname+'.tif')

            product.dispose()
            ### remove scene from folder
            logger.info("REMOVING " + f)
            if os.path.isfile(sarIn+"/"+f):
                os.remove(sarIn+"/"+f)
            logger.info("**** sar2sigma completed!" + f  + " processed**********")
        
    System.gc()



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
    if pol.area<1000:
        buff=pol.buffer(5*(pol.area)**0.5)
    else:
        buff=pol.buffer(2*(pol.area)**0.5)

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
    logger.info('Bounding box of the scene:')
    logger.info(rect.wkt)
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
