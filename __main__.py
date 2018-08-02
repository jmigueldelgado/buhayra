import sys
import logging
# import logging.config
from logging.config import dictConfig
import os
import json
import buhayra.log as log

logger = log.setup_custom_logger('root')

def main():

    logger.info("message from main!!")

    if sys.argv[1] is None:
        print("an argument is needed, for example:\nget_scenes\nrmclouds\nsar\nndwi\npolygonize\ninsert\nrecent polys\n1 month old polys\n2 months old polys\nupdate validation")
    elif sys.argv[1]=="getscenes":
        import buhayra.scenes as scenes
        scenes.getscenes()
    elif sys.argv[1]=="rmclouds":
        print("remove clouds\n")
        import ndwi2watermask.cloudmask as clouds
        clouds.rmclouds()
    elif sys.argv[1]=="sar":
        print("processing sar scene and thresholding\n")
        import sar2watermask.sar as sar
        sar.sar2w()
    elif sys.argv[1]=="ndwi":
        print("processing scene and computing ndwi\n")
        import ndwi2watermask.ndwi as n2w
        n2w.ndwi2watermask()
    elif sys.argv[1]=="polygonize":
        print("polygonizing water rasters\n")
        import buhayra.polygonize as polly
        polly.polygonize()
    elif sys.argv[1]=="insert":
        print("inserting into mongodb\n")
        import buhayra.insertPolygons as ipol
        #f = open('insert.log', 'w')
        #try:
        ipol.insertPolygons()
        #except Exception, e:
        #    f.write('An exceptional thing happed - %s' % e)
        #f.close()
    elif sys.argv[1]=="recent polys":
        print("obtain most recent polygons from mongodb\n")
        import buhayra.getLatestPolygons as gLP
        gLP.connect_and_get(0)
    elif sys.argv[1]=="1 month old polys":
        print("obtain last month's polygons from mongodb\n")
        import buhayra.getLatestPolygons as gLP
        gLP.connect_and_get(1)
    elif sys.argv[1]=="2 months old polys":
        print("obtain polygons from 2 months ago from mongodb\n")
        import buhayra.getLatestPolygons as gLP
        gLP.connect_and_get(2)
    elif sys.argv[1]=="update validation":
        print("obtain validation dataset from funceme api\n")
        import buhayra.funceme as fcm
        fcm.insert_insitu_monitoring()
    elif sys.argv[1]=="test":
        # print("tests environment\n")
        import ndwi2watermask.ndwi as n2w
        n2w.test_one_ndwi()
    elif sys.argv[1]=="another test":
        # print("tests environment\n")
        #print("test!!!!\n")
        import buhayra.testlog as tl
        tl.testing_logging()
    else:
        print('please provide one of "rmclouds", "getscenes" or "ndwi"')


if __name__ == "__main__":
    main()
