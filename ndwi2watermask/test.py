import zipfile
import subprocess
import os
import numpy as np
import re
from rasterio.warp import reproject,Resampling
from affine import Affine
import rasterio as rio

def interpolate_clouds_to_10m(file_clouds):
    print('interpolate_clouds_to_10m:\n')
    print('Open files, reserve memory:\n')
    dataset_clouds = rio.open(file_clouds)
    clouds = dataset_clouds.read(1)
    clouds10 = np.empty(shape=(int(round(clouds.shape[0] * 2)),
        int(round(clouds.shape[1] * 2))))
    print('define transformation:\n')

    aff = dataset_clouds.transform
    newaff = Affine(aff[0] / 2, aff[1], aff[2],aff[3], aff[4] / 2, aff[5])
    print('Reproject: \n')
    reproject(clouds, clouds10,
        src_transform = aff,
        dst_transform = newaff,
        src_crs = dataset_clouds.crs,
        dst_crs = dataset_clouds.crs,
        resampling = Resampling.nearest)

    return(clouds10)

clouds10=interpolate_clouds_to_10m('/mnt/scratch/martinsd/s2a_scenes/in/S2A_MSIL1C_20180223T130241_N0206_R095_T24MTT_20180223T192653.SAFE/GRANULE/L1C_T24MTT_A013963_20180223T130243/IMG_DATA/cloud.img')
clouds10
