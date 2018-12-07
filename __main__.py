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

        logger.error('an argument is needed, list of arguments:\n- "get scenes"\n- "get past scenes" year month\n- "sar2sigma"\n- "sar2sigma" year month\n- "threshold last" N\n- "threshold year month" year month\n- insert\n- recent polys\n- 1 month old polys\n- 2 months old polys\n- update validation')

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

        import sar2watermask.sar as sar
        f=sar.select_last_scene()
        if f is None:
            logger.info("There are no scenes to process in "+sarIn+". Exiting")
            raise SystemExit()
        sar.sar2sigma([f])

    elif sys.argv[1]=="sar2sigma year month":

        import sar2watermask.sar as sar

        scenes=sar.select_scenes_year_month(int(sys.argv[2]),int(sys.argv[3]))
        if scenes is None:
            logger.info("There are no past scenes for year "+sys.argv[2]+" and month "+sys.argv[3]+" available to process in "+sarIn+". Exiting")
            raise SystemExit()
        if len(scenes)==1:
            sar.sar2sigma([scenes])
        if len(scenes)>1:
            sar.sar2sigma(scenes)


    elif sys.argv[1]=="threshold last":

        logger.info("computing thresholds for last "+sys.argv[2]+" scenes")
        import buhayra.thresholding as thresh
        import buhayra.loops as loops
        scenes=thresh.select_n_last_tiffs(int(sys.argv[2]))
        loops.threshold_loop(scenes)


    elif sys.argv[1]=="threshold year month":

        logger.info("computing thresholds for all tiffs in "+sys.argv[2]+"-"+sys.argv[3])
        import buhayra.thresholding as thresh
        import buhayra.loops as loops
        tiffs=thresh.select_tiffs_year_month(int(sys.argv[2]),int(sys.argv[3]))
        loops.threshold_loop(tiffs)

    elif sys.argv[1]=="insert":

        logger.info("inserting into mongodb in "+sys.argv[2]+"-"+sys.argv[3])
        import buhayra.insertPolygons as ipol
        tiffs=ipol.select_tiffs_year_month(int(sys.argv[2]),int(sys.argv[3]))


        ipol.insert_loop(ipol)

    elif sys.argv[1]=="write polygons":

        logger.info("writing polygons as gpkg")
        import buhayra.insertPolygons as ipol
        ipol.write_poly_loop()

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

        import tests.test_parallel as par
        par.test_dask()

    elif sys.argv[1]=="run maintenance":

        import maintenance.run_rename as rnm
        rnm.rename_json()

    else:

        logger.error("an argument is needed, for example: get_scenes, sar, threshold, insert, recent polys, 1 month old polys, 2 months old polys, update validation")


if __name__ == "__main__":
    main()
