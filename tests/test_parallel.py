
from buhayra.thresholding import *
import dask
from dask.distributed import Client, progress, LocalCluster
cluster = LocalCluster(processes=False,n_workers=3,threads_per_worker=6)
client = Client(cluster)

load_sigma_naught=dask.delayed(load_sigma_naught)
load_metadata=dask.delayed(load_metadata)
subset_200x200=dask.delayed(subset_200x200)
determine_threshold_in_tif=dask.delayed(determine_threshold_in_tif)
threshold=dask.delayed(threshold)
save_originals=dask.delayed(save_originals)
save_watermask=dask.delayed(save_watermask)
remove_sigma_naught=dask.delayed(remove_sigma_naught)

## must also delay np.copy!!!
np.copy = dask.delayed(np.copy)

tiffs=select_n_last_tiffs(1000)

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

# total.visualize(filename='threshold.svg')
