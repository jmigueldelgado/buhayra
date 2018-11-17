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
    elif sys.argv[1]=="get scenes":
        import buhayra.scenes as scenes
        logger.info("starting scenes.getscenes(): downloading scenes from sentinel API")
        scenes.getscenes()
        logger.info("finished downloading scenes. Check info.log in home folder and inside package folder")
    elif sys.argv[1]=="sar":
        logger.info("starting sar.sar2sigma(): processing sar scene ans subsetting")
        import sar2watermask.sar as sar
        sar.sar2sigma()
        logger.info("finished sar2wm")
    elif sys.argv[1]=="threshold":
        logger.info("computing thresholds for each subset")
        import buhayra.thresholding as thresh
        thresh.threshold_loop()
    elif sys.argv[1]=="insert":
        logger.info("inserting into mongodb")
        import buhayra.insertPolygons as ipol
        ipol.insertLoop()
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
    elif sys.argv[1]=="test insert":
        import buhayra.tests as tests
        tests.testMongoConnect()
    elif sys.argv[1]=="test logging":
        import buhayra.testlog as tl
        tl.testing_logging()
    elif sys.argv[1]=="test idepix":
        import idepix.classification as ide
        ide.test()
    elif sys.argv[1]=="test parallel":
        import maintenance.test_parallel as par
        par.test()
    elif sys.argv[1]=="run maintenance":
        import maintenance.run_rename as rnm
        rnm.rename_json()
    else:
        logger.error("an argument is needed, for example: get_scenes, sar, threshold, insert, recent polys, 1 month old polys, 2 months old polys, update validation")


if __name__ == "__main__":
    main()
