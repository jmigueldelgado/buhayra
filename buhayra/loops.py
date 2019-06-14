from buhayra.getpaths import *
import buhayra.thresholding as thresh
import buhayra.polygonize as poly
import buhayra.insertPolygons as insert
import numpy as np
import logging
import rasterio
import geojson
import fiona
import os
import subprocess
import datetime


def thresh_pol_insert(tiffs,refgeoms):
    logger = logging.getLogger('root')

    with open(os.path.join(home['home'],'ogr2ogr.log'), 'a') as o_std, open(os.path.join(home['home'], 'ogr2ogr.err'), 'a') as o_err:
        ls = list()
        gj_path = os.path.join(polOut,'watermask-tmp-'+datetime.datetime.today().strftime('%Y-%m-%d_%H%M%S%f')+'.geojson')
        logger.info('polygonizing and saving to '+gj_path)

        for abs_path in tiffs:
            filename = abs_path.split('/')[-1]
            foldername = abs_path.split('/')[-2]
            try:
                sigma_naught=thresh.load_sigma_naught(abs_path)
                metadata=thresh.load_metadata(abs_path)
            except OSError as err:
                logger.info( 'Error {}'.format(err)+" when opening "+abs_path)
                continue
            except:
                logger.info("Unexpected error: "+ sys.exc_info()[0]+" when opening "+abs_path)
                continue

            splt = thresh.subset_500x500(sigma_naught)
            thr = thresh.determine_threshold_in_tif(splt)
            openwater = thresh.threshold(sigma_naught,thr)
            pol = poly.raster2shapely(openwater.astype(rasterio.int32),metadata)
            pol_in_jrc, intersection_area = poly.select_intersecting_polys(pol,refgeoms,filename)
            dict = poly.prepareDict(pol_in_jrc,filename,thr,intersection_area)
            ls.append(dict)
            open(os.path.join(abs_path[:-3]+'finished'),'w').close()

        featcoll = poly.json2geojson(ls)

        with open(gj_path,'w') as f:
            geojson.dump(featcoll,f)



        insert.insert_into_postgres(gj_path,o_std,o_err)
        logger.info('finished inserting '+gj_path)
