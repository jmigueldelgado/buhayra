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
    BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')
    f='S2A_MSIL1C_20180424T130251_N0206_R095_T24MTT_20180424T181045.zip'
    s2aIn = scratch+'/s2a_scenes/in'
    product = ProductIO.readProduct(s2aIn+"/"+f)
    logger.info('path: '+s2aIn + "/"+f)
    logger.info('product name:')
    logger.info(product.getName())
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

    ## Band Arithmetics for getting the water mask from idepix classification product

    expression = open(home['parameters'] +'/band_maths_idepix.txt',"r").read()

    targetBand1 = BandDescriptor()
    targetBand1.name = 'water'
    targetBand1.type = 'int32'
    targetBand1.expression = expression

    targetBands = jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', 1)
    targetBands[0] = targetBand1
    parameters = HashMap()
    parameters.put('targetBands', targetBands)

    product_water = GPF.createProduct('BandMaths', parameters, product_classif)

    current_bands = product_water.getBandNames()

    # for bname in current_bands:
    #     if str(bname) != 'water':
    #         b=product_classif.getBand(str(bname))
    #         if product_classif.removeBand(b):
    #             logger.info('removed band ' + str(bname))
    #         else:
    #             logger.info('could not remove band '+ str(bname)+'. Please check for bug.')
    #             sys.exit('could not remove band '+ str(bname))

    ProductIO.writeProduct(product_water,s2aOut + "/" + product_classif.getName() + '_watermask',outForm)
