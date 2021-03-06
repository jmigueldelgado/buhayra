import sys
import logging
import os
import json
import buhayra.log as log
from buhayra.getpaths import *
import buhayra.utils as utils
from shapely.geometry import mapping, Polygon, shape
import fiona
import IPython
#from IPython.core import ultratb
#sys.excepthook = ultratb.FormattedTB(mode='Verbose',
#                                     color_scheme='Linux', call_pdb=1)

logger = log.setup_custom_logger('root','INFO')

pid=os.getpid()

def main():

    logger.info("Message from __main__.py. Starting process " + str(pid)+".")

    if sys.argv[1] is None:

        logger.error('an argument is needed, list of arguments:\n- "get scenes"\n- "get past scenes" [year] [month]\n- "sar2sigma"\n- "sar2sigma" [year] [month]\n- "threshold+insert" [year] [month]\n')

    elif sys.argv[1]=="get scenes":

        import buhayra.scenes as scenes
        logger.info("starting scenes.getscenes(): downloading scenes from sentinel API")
        scenes.get_scenes()
        logger.info("finished downloading scenes. Check info.log in home folder and inside package folder")

    elif sys.argv[1]=="sar2sigma":

        import sar2watermask.sar as sar
        f=utils.select_last_scene(sarIn)
        if not f:
            logger.info("There are no scenes to process in "+sarIn+". Exiting")
            raise SystemExit()
        sar.sar2sigma_subset([f])

    elif sys.argv[1]=="sar2sigma year month":

        import sar2watermask.sar as sar

        scenes=utils.select_scenes_year_month(int(sys.argv[2]),int(sys.argv[3]),sarIn)
        if scenes is None:
            logger.info("There are no past scenes for year "+sys.argv[2]+" and month "+sys.argv[3]+" available to process in "+sarIn+". Exiting")
            raise SystemExit()
        if len(scenes)==1:
            sar.sar2sigma_subset([scenes])
        if len(scenes)>1:
            sar.sar2sigma_subset(scenes)


    elif sys.argv[1]=="edge detection year month":

        logger.info("inserting into postgreSQL in "+sys.argv[2]+"-"+sys.argv[3])
        import buhayra.image_processing as image
        Y = int(sys.argv[2])
        M = int(sys.argv[3])
        folders_in_ym = utils.select_folders_year_month(Y,M,sarOut)
        tiffs=utils.select_tiffs_year_month(Y,M,folders_in_ym)

        # prepare list of reference geometries
        with fiona.open(home['proj']+'/buhayra/auxdata/wm_utm_'+location['region']+'.gpkg','r') as wm:
            refgeoms = dict()
            for wm_feat in wm:
                # import IPython
                refgeom=shape(wm_feat['geometry'])
                refgeoms[int(wm_feat['properties']['id_jrc'])] = refgeom.buffer(0)

        # slice list of tiffs
        sizeofslice=200
        nslices = len(tiffs)//sizeofslice
        tiffslices = list()
        for i in range(nslices):
            tiffslices.append(tiffs[i*sizeofslice:(i*sizeofslice+sizeofslice)])
        tiffslices.append(tiffs[(nslices*sizeofslice):len(tiffs)])

        COUNT = 0
        for slice in tiffslices:
            logger.info('edge detection of '+str(sizeofslice) + ' tiffs. '+str(COUNT)+'of '+str(len(tiffs))+' done.')
            image.edge_detection(slice,refgeoms)
            COUNT = COUNT + sizeofslice

    elif sys.argv[1]=="concave hull and insert year month":

        logger.info("calling concaveman for "+sys.argv[2]+"-"+sys.argv[3])
        import buhayra.loops as loops
        Y = int(sys.argv[2])
        M = int(sys.argv[3])
        folders_in_ym = utils.select_folders_year_month(Y,M,sarOut)
        tiffs=utils.select_tiffs_year_month(Y,M,folders_in_ym)

        # slice list of tiffs
        sizeofslice=200
        nslices = len(tiffs)//sizeofslice
        tiffslices = list()
        for i in range(nslices):
            tiffslices.append(tiffs[i*sizeofslice:(i*sizeofslice+sizeofslice)])
        tiffslices.append(tiffs[(nslices*sizeofslice):len(tiffs)])

        # prepare list of reference geometries
        with fiona.open(home['proj']+'/buhayra/auxdata/wm_utm_'+location['region']+'.gpkg','r') as wm:
            refgeoms = dict()
            for wm_feat in wm:
                # import IPython
                refgeom=shape(wm_feat['geometry'])
                refgeoms[int(wm_feat['properties']['id_jrc'])] = refgeom.buffer(0)

        COUNT = 0
        for slice in tiffslices:
            logger.info('call concaveman in R for '+str(sizeofslice) + ' geojsons. '+str(COUNT)+'of '+str(len(tiffs))+' done.')
            loops.concaveman_insert(slice,refgeoms)
            COUNT = COUNT + sizeofslice


    elif sys.argv[1]=="threshold+insert year month":

        logger.info("inserting into postgreSQL in "+sys.argv[2]+"-"+sys.argv[3])
        import buhayra.loops as loops
        Y = int(sys.argv[2])
        M = int(sys.argv[3])
        folders_in_ym = utils.select_folders_year_month(Y,M,sarOut)
        tiffs=utils.select_tiffs_year_month(Y,M,folders_in_ym)

        # prepare list of reference geometries
        with fiona.open(home['proj']+'/buhayra/auxdata/wm_utm_'+location['region']+'.gpkg','r') as wm:
            refgeoms = dict()
            for wm_feat in wm:
                # import IPython
                # IPython.embed()
                refgeom=shape(wm_feat['geometry'])
                refgeoms[int(wm_feat['properties']['id_jrc'])] = refgeom.buffer(0)

        # slice list of tiffs
        sizeofslice=200
        nslices = len(tiffs)//sizeofslice
        tiffslices = list()
        for i in range(nslices):
            tiffslices.append(tiffs[i*sizeofslice:(i*sizeofslice+sizeofslice)])
        tiffslices.append(tiffs[(nslices*sizeofslice):len(tiffs)])

        COUNT = 0
        for slice in tiffslices:
            logger.info('thresholding '+str(sizeofslice) + ' tiffs and inserting. '+str(COUNT)+'of '+str(len(tiffs))+' done.')
            loops.thresh_pol_insert(slice,refgeoms)
            COUNT = COUNT + sizeofslice

    elif sys.argv[1]=="threshold+insert":

        logger.info("inserting recent scenes into postgreSQL")
        import buhayra.loops as loops
        from maintenance.move_stuff_around import update_db, delete_old_geoms
        #IPython.embed()
        folders_in_7days = utils.select_folders_7days(sarOut)
        tiffs=utils.select_tiffs_7days(folders_in_7days)

        logger.debug("prepare list of reference geometries")
        with fiona.open(home['proj']+'/buhayra/auxdata/wm_utm_'+location['region']+'.gpkg','r') as wm:
            refgeoms = dict()
            for wm_feat in wm:
                refgeom=shape(wm_feat['geometry'])
                refgeoms[wm_feat['properties']['id_jrc']] = refgeom.buffer(0)

        # slice list of tiffs
        sizeofslice=200
        nslices = len(tiffs)//sizeofslice
        tiffslices = list()
        for i in range(nslices):
            tiffslices.append(tiffs[i*sizeofslice:(i*sizeofslice+sizeofslice)])
        tiffslices.append(tiffs[(nslices*sizeofslice):len(tiffs)])

        COUNT = 0
        for slice in tiffslices:
            logger.info('thresholding '+str(sizeofslice) + ' tiffs and inserting geometries and attribute data into database region_geom. '+str(COUNT)+'of '+str(len(tiffs))+' done.')
            loops.thresh_pol_insert(slice,refgeoms)
            COUNT = COUNT + sizeofslice

        logger.info('updating database region with attribute data but no geometries')
        update_db()
        logger.info('hoping all went well while commiting to the psql')
        logger.info('now deleting old geoms from table *_geom')
        delete_old_geoms()
        logger.info('hoping all went well with deleting old geoms')


    elif sys.argv[1]=="move stuff around":

        import maintenance.move_stuff_around as mvstuff
        # mnt.move_tifs_to_folders()
        mvstuff.move_proc(int(sys.argv[2]),int(sys.argv[3]))

    elif sys.argv[1]=="hav":

        import buhayra.hav as hav
        # mnt.move_tifs_to_folders()
        hav.extract_HAV()

    elif sys.argv[1]=="imerg":
        # download imerg files
        import buhayra.assim as assim
        ref_date=date.today()-3
        ref_strg='{:4d}'.format(ref_date.year)+'{:02d}'.format(ref_date.month)+'{:02d}'.format(ref_date.day)
        imerg_home='https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGDE.06/' + '{:4d}'.format(ref_date.year) + '/' + '{:02d}'.format(ref_date.month)
        imerg_url=imerg_home + '3B-DAY-E.MS.MRG.3IMERG.'+ ref_strg + '-S000000-E235959.V06.nc4'
        assim.download_from_url(imerg_url,file_path=home['scratch']+'/imerg/'+imerg_url.split('/')[-1])
    elif sys.argv[1]=="remove finished scenes":
        import maintenance.move_stuff_around as mvstuff
        mvstuff.rm_finished(sarIn)

    else:

        logger.error('an argument is needed, list of arguments:\n- "get scenes"\n- "get past scenes" [year] [month]\n- "sar2sigma"\n- "sar2sigma" [year] [month]\n- "threshold+insert" [year] [month]\n')


if __name__ == "__main__":
    main()
