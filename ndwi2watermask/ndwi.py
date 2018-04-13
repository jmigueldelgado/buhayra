import rasterio.mask
from ndwi2watermask.cloudmask import list_pols,merge_pols,unzipJp2,unzipMasks,getBandDir
import fiona
import glob
import rasterio as rio
import zipfile
import os
import buhayra.getpaths as pths
import numpy as np
import re
from shutil import rmtree
import json
from rasterio.features import shapes
## some exercises with geotiffs:

#scene='/home/delgado/scratch/s2a_scenes/out/S2A_MSIL1C_20180223T130241_N0206_R095_T24MTT_20180223T192653.tif'
#dataset = rio.open(scene)

## this is not working in current version of rasterio (0.36)
#with rio.open(scene) as src:
#    w = src.read(1, window=Window(0, 0, 10, 10))

#dataset.crs
#band3 = dataset3.read(1)


### some exercises with matrices to make sure everything is working below
#ar=np.random.random_integers(0,100,2500)
#ar.shape=(50,50)
#np.sum(ar > -1)
#ar_out[ar<50] =

#ar_bool.shape

#ar[ar_bool] = 0
#ar.shape
#pths.s2aIn="/home/delgado/Documents/tmp"
#pths.s2aOut="/home/delgado/Documents/tmp"
def ndwi2watermask():
    print("Executing ndwi2watermask()...")
    items=os.listdir(pths.s2aIn)
    for item in items:
        scenename=item
        print("----",scenename,"----\n")
        item=pths.s2aIn + '/' + item
        if re.search('^.*\.zip$', item):
            sceneJp2 = unzipJp2(item)
            sceneMasks = unzipMasks(item)

            ### use nodata and clouds as masks
            masks = list_pols(sceneMasks)

            scene=sceneJp2[0].split(".SAFE/GRANULE")[0]
            banddir = getBandDir(sceneJp2)
            maskdir = getBandDir(sceneMasks)

            p3 = glob.glob(banddir + '/*B03.jp2')
            p8 = glob.glob(banddir + '/*B08.jp2')

            ### the product is provided as a uint16.
            ### usually one could divide by 1000 to get the real TOA values,
            ### but since we are interested in the index, there is no need for that
            print("Opening band 3\n")
            dataset3 = rio.open(p3[0])
            if len(masks>0):
                band3, out_transform =rio.mask.mask(dataset3,masks,all_touched=True,invert=True)
            else:
                band3 = dataset3.read(1)
            band3 = band3.astype(float)

            print("Opening band 8\n")
            dataset8 = rio.open(p8[0])
            if len(masks>0):
                band8, out_transform =rio.mask.mask(dataset8,masks,all_touched=True,invert=True)
            else:
                band8 = dataset8.read(1)
            band8 = band8.astype(float)
            print("Computing NDWI\n")


            ### the threshold must be set here, because if it is lower than 0, it messes up with the mask
            thresh=-0.1
            NDWI = (band3-band8)/(band3+band8)-thresh
            ndwi_bool = NDWI > 0

            ndwi_int=NDWI.astype('int16')
            ndwi_int[:]=0
            ndwi_int[ndwi_bool]=1

            out_meta = dataset3.meta.copy()

        # save the resulting raster
            out_meta.update({"driver": "GTiff",
                "height": ndwi_int.shape[1],
                "width": ndwi_int.shape[2],
                "transform": out_transform,
                "dtype": 'int16'})
            with rasterio.open(pths.s2aOut + '/' + scenename[:-4] + '_watermask.tif' , "w", **out_meta) as dest:
                dest.write(ndwi_int)

            ### polygonize is still now working quite well...
#            lpols = shapes(ndwi_int)
#            ndwi_int

#            list(lpols)
            os.remove(item)
            rmtree(item[:-4]+'.SAFE')
