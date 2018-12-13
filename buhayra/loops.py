from buhayra.getpaths import *
import buhayra.thresholding as thresh
import buhayra.vegetatedwater as veggie
import numpy as np
import logging
import time
import dask.array as da
# from dask_ml.decomposition import PCA
from sklearn.decomposition import PCA
from dask import compute, delayed
import dask.threaded
import rasterio

f=veggie.select_last_tiff()
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
    for f in tiffs:
        out_db=thresh.load_sigma_naught(f)
        metadata=thresh.load_metadata(f)

        original = np.copy(out_db)

        splt = thresh.subset_200x200(out_db)
        thr = thresh.determine_threshold_in_tif(splt)
        openwater = thresh.threshold(out_db,thr)

        orig = thresh.save_originals(f,original,metadata,thr)
        out.append(orig)
        wm = thresh.save_watermask(orig,openwater,metadata,thr)
        out.append(wm)
        rm = thresh.remove_sigma_naught(wm)
        out.append(rm)

    logger.info('finished threshold loop. processed '+str(len(tiffs)) + ' tifs')
