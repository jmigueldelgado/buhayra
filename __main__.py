import sys
import logging
# import logging.config
from logging.config import dictConfig
import os
import json
import buhayra.log as log

logger = log.setup_custom_logger('root','INFO')

def main():

    logger.info("Message from __main__.py. Starting process.")

    if sys.argv[1] is None:
        logger.error("an argument is needed, for example: get_scenes, rmclouds, sar, ndwi, polygonize, insert, recent polys, 1 month old polys, 2 months old polys, update validation")
    elif sys.argv[1]=="getscenes":
        import buhayra.scenes as scenes
        logger.info("starting scenes.getscenes(): downloading scenes from sentinel API")
        scenes.getscenes()
        logger.info("finished downloading scenes. Check info.log in home folder and inside package folder")
    elif sys.argv[1]=="rmclouds":
        logger.info("starting clouds.rmclouds(): cloud removing")
        import ndwi2watermask.cloudmask as clouds
        clouds.rmclouds()
        logger.info("finished cloud removing")
    elif sys.argv[1]=="sar":
        logger.info("starting sar.sar2w(): processing sar scene and thresholding")
        import sar2watermask.sar as sar
        sar.sar2w()
        logger.info("finished sar2wm")
    elif sys.argv[1]=="ndwi":
        logger.info("processing scene and computing ndwi")
        import ndwi2watermask.ndwi as n2w
        n2w.ndwi2watermask()
    elif sys.argv[1]=="polygonize":
        logger.info("polygonizing water rasters")
        import buhayra.polygonize as polly
        polly.polygonize()
    elif sys.argv[1]=="insert":
        logger.info("inserting into mongodb")
        import buhayra.insertPolygons as ipol
        #f = open('insert.log', 'w')
        #try:
        ipol.insertPolygons()
        #except Exception, e:
        #    f.write('An exceptional thing happed - %s' % e)
        #f.close()
    elif sys.argv[1]=="recent polys":
        logger.info("obtain most recent polygons from mongodb")
        import buhayra.getLatestPolygons as gLP
        gLP.connect_and_get(0)
    elif sys.argv[1]=="1 month old polys":
        logger.info("obtain last month's polygons from mongodb")
        import buhayra.getLatestPolygons as gLP
        gLP.connect_and_get(1)
    elif sys.argv[1]=="2 months old polys":
        logger.info("obtain polygons from 2 months ago from mongodb")
        import buhayra.getLatestPolygons as gLP
        gLP.connect_and_get(2)
    elif sys.argv[1]=="3 months old polys":
        logger.info("obtain polygons from 3 months ago from mongodb")
        import buhayra.getLatestPolygons as gLP
        gLP.connect_and_get(3)
    elif sys.argv[1]=="update validation":
        logger.info("obtain validation dataset from funceme api")
        import buhayra.funceme as fcm
        fcm.insert_insitu_monitoring()
    elif sys.argv[1]=="test":
        import ndwi2watermask.ndwi as n2w
        n2w.test_one_ndwi()
    elif sys.argv[1]=="test insert":
        import buhayra.insertPolygons as insPol
        insPol.testMongoConnect()
    elif sys.argv[1]=="test logging":
        import buhayra.testlog as tl
        tl.testing_logging()
    else:
        logger.error("an argument is needed, for example: get_scenes, rmclouds, sar, ndwi, polygonize, insert, recent polys, 1 month old polys, 2 months old polys, update validation")


if __name__ == "__main__":
    main()
