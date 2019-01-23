from buhayra.getpaths import *
import buhayra.thresholding as thresh
import buhayra.polygonize as poly
import buhayra.insertPolygons as insert
import buhayra.vegetatedwater as veggie
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
        gj_path = os.path.join(polOut,'watermask-tmp-'+datetime.datetime.today().strftime('%Y-%m-%d_%H%M%S')+'.geojson')

        for abs_path in tiffs:
            filename = abs_path.split('/')[-1]
            foldername = abs_path.split('/')[-2]
            sigma_naught=thresh.load_sigma_naught(abs_path)
            metadata=thresh.load_metadata(abs_path)

            splt = thresh.subset_200x200(sigma_naught)
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

            logger.info('inserting ' + gj_path)
            insert.insert_into_postgres_NEB(gj_path,o_std,o_err)
            logger.info('finished insert ' + gj_path)


# f=veggie.select_last_tiff()
def glcm_loop(scenes):
    window_shape=(3,3)
    logger = logging.getLogger('root')
    for f in scenes:
        with rasterio.open(vegIn + '/' +f,'r') as ds:
            x=da.from_array(ds.read(1),(round(ds.shape[0]/5), round(ds.shape[1]/5)))
        X_std = (x - np.amin(x)) / (np.amax(x) - np.amin(x))
        X_scaled = dask.array.round(X_std * (255 - 0) + 0)
        xuint = X_scaled.astype('uint8')
        new_image = image[:-(image.shape[0]%window_shape[0]),:-(image.shape[1]%window_shape[1])]

        #calculate dimensions of list of 3x3 blocks
        newshape = new_image.shape
        nblocks = int(newshape[0]/3) * (newshape[1]/3)

        lazypredictors = da.map_blocks(veggie.glcm_predictors,xuint,window_shape,chunks=(round(nblocks/25),8))
        predictors = compute(lazypredictors, scheduler='threads')

        pca = PCA(n_components=5)
        lazypca=pca.fit(lazypredictors)



def threshold_loop(tiffs):
    logger = logging.getLogger('root')
    out=list()
    for filename in tiffs:
        sigma_naught=thresh.load_sigma_naught(filename)
        metadata=thresh.load_metadata(filename)

        original = np.copy(sigma_naught)

        splt = thresh.subset_200x200(sigma_naught)
        thr = thresh.determine_threshold_in_tif(splt)
        openwater = thresh.threshold(sigma_naught,thr)

        # orig = thresh.save_originals(f,original,metadata,thr)
        orig = thresh.flag_originals(f,metadata,thr)
        out.append(orig)
        wm = thresh.save_watermask(orig,openwater,metadata,thr)
        out.append(wm)
        # rm = thresh.remove_sigma_naught(wm)
        # out.append(rm)

    logger.info('finished threshold loop. processed '+str(len(tiffs)) + ' tifs')


def insert_loop(tiffs):
    logger = logging.getLogger('root')
    # cluster = LocalCluster(processes=False,n_workers=1,threads_per_worker=2)
    # client = Client(cluster)

    # load_watermask=dask.delayed(load_watermask)
    # load_metadata=dask.delayed(load_metadata)
    # raster2shapely=dask.delayed(raster2shapely)
    # prepareJSON=dask.delayed(prepareJSON)
    # select_intersecting_polys=dask.delayed(select_intersecting_polys)
    # insert_into_NEB=dask.delayed(insert_into_NEB)
    # remove_watermask=dask.delayed(remove_watermask)

    logger = logging.getLogger('root')
    neb = insert.connect_to_NEB()
    out=list()
    with fiona.open(home['home']+'/proj/buhayra/buhayra/auxdata/wm_utm_simplf.gpkg','r') as wm:
        for f in tiffs:
            r = poly.load_watermask(f)
            metadata = poly.load_metadata(f)
            poly = poly.raster2shapely(r,metadata)
            feat = poly.prepareJSON(poly,f,metadata)
            feat_wm = poly.select_intersecting_polys(feat,wm)
            feat_id = insert.insert_into_NEB(feat_wm,neb)

            out.append(feat_id)
            rm = poly.remove_watermask(f,feat_id)
            out.append(rm)

            # orig = thresh.flag_originals(f,metadata,thr)
            # out.append(orig)
