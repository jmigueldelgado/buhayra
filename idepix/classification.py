import numpy as np
import re
# import rasterio as rio
from os import listdir
import os
import datetime
import sys
import xml.etree.ElementTree
import zipfile
import snappy
from snappy import Product
from snappy import ProductData
from snappy import ProductUtils
from snappy import FlagCoding
from snappy import GPF
from snappy import ProductIO
from snappy import jpy
from snappy import HashMap
from snappy import Rectangle
import logging
from buhayra.getpaths import *

def test():
    logger = logging.getLogger('root')
    outForm='GeoTIFF+XML'
    WKTReader = snappy.jpy.get_type('com.vividsolutions.jts.io.WKTReader')
    HashMap = snappy.jpy.get_type('java.util.HashMap')
    f='S2A_MSIL1C_20180424T130251_N0206_R095_T24MTT_20180424T181045.zip'
    s2aIn = '/home/delgado/scratch/s2a_scenes/in'
    product = ProductIO.readProduct(s2aIn+"/"+f)
    band_names = product.getBandNames()
    logger.debug('example of band names:')
    logger.debug(band_names[0])

    logger.info('getDefaultInstance')
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

    params = HashMap()
    root = xml.etree.ElementTree.parse(home['parameters']+'/resample.xml').getroot()
    logger.debug('importing parameter file for resampling. parameters:')
    for child in root:
        logger.debug(child.text)
        params.put(child.tag,child.text)

    logger.info('...now resample:')
    product_resampled=GPF.createProduct('Resample', params, product)

    params = HashMap()
    root = xml.etree.ElementTree.parse(home['parameters']+'/idepix.xml').getroot()
    logger.debug('importing parameter file for idepix. parameters:')
    for child in root:
        logger.debug(child.text)
        params.put(child.tag,child.text)
    logger.info('apply idepix classification')
    product_classif = GPF.createProduct('Idepix.Sentinel2', params, product_resampled)
    current_bands = product_classif.getBandNames()
    current_bands[0]
    ProductIO.writeProduct(product_classif,s2aOut + "/" + product_classif.getName() + '_classified',outForm)
