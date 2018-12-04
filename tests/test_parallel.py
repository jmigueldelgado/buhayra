
from buhayra.thresholding import *
# import dask
# from dask.distributed import Client, progress
#
# load_sigma_naught=dask.delayed(load_sigma_naught)
# load_metadata=dask.delayed(load_metadata)
# subset_200x200=dask.delayed(subset_200x200)
# determine_threshold_in_tif=dask.delayed(determine_threshold_in_tif)
# threshold=dask.delayed(threshold)
# save_originals=dask.delayed(save_originals)
# save_watermask=dask.delayed(save_watermask)

tiffs=select_n_last_tiffs(5)
out=list()
for f in tiffs:
    out_db=load_sigma_naught(f)
    metadata=load_metadata(f)

    original = np.copy(out_db)
    splt = subset_200x200(out_db)
    thr = determine_threshold_in_tif(splt)
    openwater = threshold(out_db,thr)

    save_originals(f,original,metadata,thr)
    f=save_watermask(f,openwater,metadata,thr)
    out.append(f)
#    remove_sigma_naught(f)

client = Client(threads_per_worker=4, n_workers=1)
client
f.compute()
out
polOut
