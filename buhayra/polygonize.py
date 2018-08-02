import os
import subprocess
import glob
import datetime
from buhayra.getpaths import *
import logging

def polygonize():
    logger = logging.getLogger('root')

    t0=datetime.datetime.now()

    logger.info("polygonize SAR")

    items=os.listdir(sarOut)
    newlist = []
    for names in items:
        if names.endswith("watermask.tif"):
            newlist.append(names[:-4])

    #newlist = list(set(newlist))
    #newlist
    #scene=newlist[0]

    for scene in newlist:

        logger.info("\n polygonizing " + scene + "\n")
        out_gml = scene + ".gml"
        subprocess.call([pyt,gdalPol,sarOut + "/" + scene + ".tif","-f","GML",polOut + "/" + out_gml])
        os.remove(sarOut + "/" + scene + ".tif")

    logger.info("sentinel-1 polygonize completed!" + str(len(newlist))  + " watermasks processed")
    logger.info("Elapsed time: " + str(datetime.datetime.now()-t0))




    ####################################################################################
    ######### polygonize S2A


    logger.info("... now polygonize S2A")

    items=os.listdir(s2aOut)

    for scene in items:
        logger.info("\n polygonizing " + scene)
        out_gml = scene[:-4] + "_watermask.gml"
        subprocess.call([pyt,gdalPol,s2aOut + "/" + scene,"-f","GML",polOut + "/" + out_gml])
        os.remove(s2aOut + "/" + scene)

    logger.info("sentinel-2 polygonize completed!" + str(len(items))  + " watermasks processed")
    logger.info("Elapsed time: " + str(datetime.datetime.now()-t0))
    logger.info("End of poligonize")
