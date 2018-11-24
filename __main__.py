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
        scenes.get_scenes()
        logger.info("finished downloading scenes. Check info.log in home folder and inside package folder")

    elif sys.argv[1]=="get past scenes":

        import buhayra.scenes as scenes
        logger.info("starting scenes.getscenes(): downloading scenes from sentinel API")
        scenes.get_past_scenes(int(sys.argv[2]),int(sys.argv[3]))
        logger.info("finished downloading scenes. Check info.log in home folder and inside package folder")

    elif sys.argv[1]=="sar2sigma":

        logger.info("starting sar.sar2sigma(): processing sar scenes and subsetting")
        import sar2watermask.sar as sar
        f=sar.select_last_scene()
        if f is None:
            logger.info("There are no scenes to process in "+sarIn+". Exiting")
            raise SystemExit()
        sar.sar2sigma([f])
        logger.info("finished sar2wm")

    elif sys.argv[1]=="sar2sigma year month":

        logger.info("starting sar.sar2sigma() in parallel: processing past sar scenes and subsetting")
        import sar2watermask.sar as sar

        scenes=sar.select_scenes_year_month(int(sys.argv[2]),int(sys.argv[3]))
        if scenes is None:
            logger.info("There are no past scenes for year "+sys.argv[2]+" and month "+sys.argv[3]+" available to process in "+sarIn+". Exiting")
            raise SystemExit()
        logger.info("entering for loop")
        if len(scenes)==1:
            sar.sar2sigma([scenes])
        if len(scenes)>1:
            sar.sar2sigma(scenes)

        logger.info("finished sar2wm")

    elif sys.argv[1]=="threshold last":

        logger.info("computing thresholds for last "+sys.argv[2]+" scenes")
        import buhayra.thresholding as thresh
        scenes=thresh.select_n_last_tiffs(int(sys.argv[2]))
        thresh.threshold_loop(scenes)


    elif sys.argv[1]=="threshold year month":

        logger.info("computing thresholds for all tiffs in "+sys.argv[2]+"-"+sys.argv[3])
        import buhayra.thresholding as thresh
        tiffs=thresh.select_tiffs_year_month(int(sys.argv[2]),int(sys.argv[3]))
        thresh.threshold_loop(tiffs)

    elif sys.argv[1]=="insert":

        logger.info("inserting into mongodb")
        import buhayra.insertPolygons as ipol
        ipol.insertLoop()

    elif sys.argv[1]=="recent polys":

        logger.info("obtain most recent polygons from mongodb")
        import buhayra.getLatestPolygons as gLP
        gLP.connect_and_get(int(sys.argv[2]))

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
