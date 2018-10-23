from os import listdir
#import os
import datetime
import sys
import numpy
import logging

from buhayra.getpaths import *


#############################


#############################################
# MAKE SURE YOU SET THE NECESSARY RAM
# MEMORY (MORE THAN 10G) IN THE FOLLOWING VARIABLES BEFORE CALLING THIS SCRIPT
# _JAVA_OPTIONS
# JAVA_TOOL_OPTIONS
# ##########################################

# Some definitions


def sar2w():
    logger = logging.getLogger('root')

    if(len(listdir(sarIn))<1):
        logger.info(sarIn+" is empty! Nothing to do. Exiting and returning None.")
        return None

    import xml.etree.ElementTree
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

    logger = logging.getLogger('root')
    t0=datetime.datetime.now()

    logger.info("importing functions from snappy")

    outForm='GeoTIFF+XML'
    WKTReader = snappy.jpy.get_type('com.vividsolutions.jts.io.WKTReader')
    HashMap = snappy.jpy.get_type('java.util.HashMap')
    SubsetOp = snappy.jpy.get_type('org.esa.snap.core.gpf.common.SubsetOp')
    Point = snappy.jpy.get_type('java.awt.Point')
    Dimension = snappy.jpy.get_type('java.awt.Dimension')
    System = jpy.get_type('java.lang.System')
    BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')
    logger.debug(WKTReader)
    logger.debug(HashMap)
    logger.debug(BandDescriptor)
    logger.debug(System)

    f=listdir(sarIn)[0]
    product = ProductIO.readProduct(sarIn+"/"+f)
    logger.info("processing " + f)

    # Obtain some attributes

    height = product.getSceneRasterHeight()
    width = product.getSceneRasterWidth()
    name = product.getName()
    description = product.getDescription()
    band_names = product.getBandNames()

    # Initiate processing
    logger.info("start processing")

    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

    # Subset into 4 pieces

    size = product.getSceneRasterSize()

    p_ul = Point(1000,0)
    p_ur = Point(size.width/2,0)
    p_ll = Point(1000,size.height/2)
    p_lr = Point(size.width/2,size.height/2)

    subsetDim = Dimension(size.width/2-1000,size.height/2)

    r_ul = Rectangle(p_ul,subsetDim)
    r_ur = Rectangle(p_ur,subsetDim)
    r_ll = Rectangle(p_ll,subsetDim)
    r_lr = Rectangle(p_lr,subsetDim)

    rect=[r_ul,r_ur,r_ll,r_lr]
    r=r_ul
    for r in rect:
        ##### process upper left only as an example
        #params = HashMap()
        #params.put('copyMetadata', True)
        #params.put('Region', r_ul)
        #product_subset = GPF.createProduct('Subset',params,product)

        op = SubsetOp()
        op.setSourceProduct(product)
        op.setCopyMetadata(True)
        op.setRegion(r)
        product_subset = op.getTargetProduct()
        labelSubset = "x" + r.x.__str__() + "_y" + r.y.__str__()


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

        ## Band Arithmetics 1

        expression = open(home['parameters'] +'/band_maths1.txt',"r").read()

        targetBand1 = BandDescriptor()
        targetBand1.name = 'watermask'
        targetBand1.type = 'float32'
        targetBand1.expression = expression

        targetBands = jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', 1)
        targetBands[0] = targetBand1

        parameters = HashMap()
        parameters.put('targetBands', targetBands)

        CalSfWater = GPF.createProduct('BandMaths', parameters, CalSf)

        current_bands = CalSfWater.getBandNames()
        logger.debug("Current Bands after Band Arithmetics 2:   %s" % (list(current_bands)))


        ## Geometric correction

        params = HashMap()
        root = xml.etree.ElementTree.parse(home['parameters']+'/terrain_correction.xml').getroot()
        for child in root:
            params.put(child.tag,child.text)

        CalSfWaterCorr1 = GPF.createProduct('Terrain-Correction',params,CalSfWater)

        current_bands = CalSfWaterCorr1.getBandNames()
        logger.debug("Current Bands after Terrain Correction:   %s" % (list(current_bands)))

        ## Band Arithmetics 2

        expression = open(home['parameters']+'/band_maths2.txt',"r").read()
        #band_names = CalSfWaterCorr1.getBandNames()
        #print("Bands:   %s" % (list(band_names)))


        targetBand1 = BandDescriptor()
        targetBand1.name = 'watermask_corr'
        targetBand1.type = 'int8'
        targetBand1.expression = expression

        targetBands = jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', 1)
        targetBands[0] = targetBand1

        parameters = HashMap()
        parameters.put('targetBands', targetBands)

        CalSfWaterCorr2 = GPF.createProduct('BandMaths', parameters, CalSfWaterCorr1)

        current_bands = CalSfWaterCorr2.getBandNames()
        logger.debug("Current Bands after Band Arithmetics 2:   %s" % (list(current_bands)))


        ### write output
        ProductIO.writeProduct(CalSfWaterCorr2,sarOut+"/"+product.getName() + "_" + labelSubset + "_watermask",outForm)

        ### release products from memory
        product_subset.dispose()
        CalSf.dispose()
        CalSfWater.dispose()
        CalSfWaterCorr1.dispose()
        CalSfWaterCorr2.dispose()
        product.dispose()
        System.gc()

        ### remove scene from folder
        logger.info("REMOVING " + f)

        os.remove(sarIn+"/"+f)

    logger.info("**** sar2watermask completed!" + f  + " processed\n********** Elapsed time: " + str(datetime.datetime.now()-t0) + "****")
