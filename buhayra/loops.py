from buhayra.getpaths import *
import os
import subprocess
import datetime
import IPython
import logging

def thresh_pol_insert(tiffs,refgeoms):
    import buhayra.thresholding as thresh
    import buhayra.polygonize as poly
    import buhayra.image_processing as image
    import numpy as np
    import rasterio
    import geojson
    import fiona
    import pyproj
    import buhayra.insertPolygons as insert
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
            pol = image.raster2shapely(openwater.astype(rasterio.int32),metadata)
            pol_in_jrc, intersection_area = poly.select_intersecting_polys(pol,refgeoms,filename)
            dict = poly.prepareDict(pol_in_jrc,filename,thr,intersection_area)
            ls.append(dict)
            open(os.path.join(abs_path[:-3]+'finished'),'w').close()

        featcoll = poly.json2geojson(ls)

        with open(gj_path,'w') as f:
            geojson.dump(featcoll,f)



        insert.insert_into_postgres(gj_path,o_std,o_err)
        logger.info('finished inserting '+gj_path)

def thresh_data_insert(tiffs,refgeoms):
    import buhayra.thresholding as thresh
    import buhayra.polygonize as poly
    import buhayra.image_processing as image
    import numpy as np
    import rasterio
    import geojson
    import fiona
    import pyproj

    import buhayra.insertPolygons as insert
    logger = logging.getLogger('root')

    ls = list()

    for abs_path in tiffs:
        filename = abs_path.split('/')[-1]
        foldername = abs_path.split('/')[-2]
        try:
            sigma_naught=thresh.load_sigma_naught(abs_path)
            metadata=thresh.load_metadata(abs_path)
        except:
            logger.info("Unexpected error: "+ sys.exc_info()[0]+" when opening "+abs_path)
            continue

        splt = thresh.subset_500x500(sigma_naught)
        thr = thresh.determine_threshold_in_tif(splt)
        openwater = thresh.threshold(sigma_naught,thr)
        pol = image.raster2shapely(openwater.astype(rasterio.int32),metadata)
        # IPython.embed()
        pol_in_jrc, intersection_area = poly.select_intersecting_polys(pol,refgeoms,filename)
        dict = poly.prepareDict(pol_in_jrc,filename,thr,intersection_area)
        ls.append(dict['properties'])
        open(os.path.join(abs_path[:-3]+'finished'),'w').close()

    insert_statement=insert.insert_into_postgres_no_geom(ls)


    logger.info('finished classifying and inserting batch of tiffs')

def edge_detection(tiffs,refgeoms):
    import buhayra.polygonize as poly
    import buhayra.image_processing as image
    import numpy as np
    import rasterio
    import geojson
    import fiona
    import pyproj
    logger = logging.getLogger('root')
    wgs84 = pyproj.CRS('EPSG:4326')
    utm = pyproj.CRS('EPSG:32724')
    utm2wgs84 = pyproj.Transformer.from_crs(utm,wgs84, always_xy=True).transform
    for abs_path in tiffs:
        tif_filename = os.path.split(abs_path)[-1]
        productName='_'.join(tif_filename[:-4].split('_')[:9])
        if os.path.exists(os.path.join(edgeOut,productName,tif_filename[:-4]+'_projected_edges.finished')) | os.path.exists(os.path.join(edgeOut,productName,tif_filename[:-4]+'_NA_SAR.finished')):
            continue
#        IPython.embed()
        id = image.edge_classification(tif_filename)
        if id == -1:
            open(os.path.join(edgeOut,productName,tif_filename[:-4]+'_NA_SAR.finished'),'w').close()
            continue
        skeleton , out_transform = image.morphological_transformations(tif_filename,refgeoms[int(id)],utm2wgs84)
        geojson_file_name=image.save_edge_coordinates(skeleton,tif_filename,out_transform)
        open(os.path.join(edgeOut,productName,tif_filename[:-4]+'_projected_edges.finished'),'w').close()


def concaveman_insert(tiffs,refgeoms):
    import geojson
    import buhayra.concaveman as concave
    import buhayra.insertPolygons as insert
    import buhayra.polygonize as poly
    logger = logging.getLogger('root')

    with open(os.path.join(home['home'],'ogr2ogr.log'), 'a') as o_std, open(os.path.join(home['home'], 'ogr2ogr.err'), 'a') as o_err:
        ls = list()
        gj_path = os.path.join(polOut,'watermask-tmp-'+datetime.datetime.today().strftime('%Y-%m-%d_%H%M%S%f')+'.geojson')
        logger.info('drawing concave hull and saving to '+gj_path)

        ls = list()

        for abs_path in tiffs:
            filename = os.path.split(abs_path)[-1][:-3] + 'geojson'
            productName='_'.join(filename[:-8].split('_')[:9])
            if os.path.exists(os.path.join(edgeOut,productName,filename[:-8]+'_concave_hull.geojson')) | os.path.exists(os.path.join(edgeOut,productName,filename[:-8]+'_NA_SAR.finished')) | os.path.exists(os.path.join(edgeOut,productName,filename[:-8]+'_empty_geometry.geojson')):
                continue
            try:
                pol = concave.concave_hull(filename,os.path.join(edgeOut,productName))
            except:
                logger.info("Unexpected error: "+ str(sys.exc_info()[0])+" when opening "+abs_path)
                continue
            pol_in_jrc, intersection_area = poly.select_intersecting_polys(pol,refgeoms,filename)
            dict = poly.prepareDict(pol_in_jrc,filename,999,intersection_area)
            ls.append(dict)
            open(os.path.join(edgeOut,productName,filename[:-8]+'_concave_hull.finished'),'w').close()
            # IPython.embed()
        featcoll = poly.json2geojson(ls)

        with open(gj_path,'w') as f:
            geojson.dump(featcoll,f)

        insert.insert_into_postgres(gj_path,o_std,o_err)
        logger.info('finished inserting '+gj_path)
