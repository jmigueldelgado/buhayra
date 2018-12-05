#from dask import compute, delayed
#import dask.multiprocessing
import dask
from dask.distributed import Client, progress, LocalCluster
import buhayra.thresholding as thresh
import numpy as np
import logging

def threshold_loop(tiffs):
    logger = logging.getLogger('root')
    cluster = LocalCluster(processes=False,n_workers=1,threads_per_worker=2)
    client = Client(cluster)

    load_sigma_naught=dask.delayed(thresh.load_sigma_naught)
    load_metadata=dask.delayed(thresh.load_metadata)
    subset_200x200=dask.delayed(thresh.subset_200x200)
    determine_threshold_in_tif=dask.delayed(thresh.determine_threshold_in_tif)
    threshold=dask.delayed(thresh.threshold)
    save_originals=dask.delayed(thresh.save_originals)
    save_watermask=dask.delayed(thresh.save_watermask)
    remove_sigma_naught=dask.delayed(thresh.remove_sigma_naught)

    # must also delay np.copy!!!
    np.copy = dask.delayed(np.copy)
    tiffs=thresh.select_n_last_tiffs(10)
    tiffs
    out=list()
    for f in tiffs:
        out_db=load_sigma_naught(f)
        metadata=load_metadata(f)

        original = np.copy(out_db)

        splt = subset_200x200(out_db)
        thr = determine_threshold_in_tif(splt)
        openwater = threshold(out_db,thr)

        orig = save_originals(f,original,metadata,thr)
        out.append(orig)
        wm = save_watermask(orig,openwater,metadata,thr)
        out.append(wm)
        rm = remove_sigma_naught(wm)
        out.append(rm)


        total=dask.delayed()(out)
        total.compute()

    logger.info('finished threshold loop. processed '+str(len(tiffs)) + ' tifs')
