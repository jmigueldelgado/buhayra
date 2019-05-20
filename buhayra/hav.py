import rasterio as rio
import rasterio.mask
import fiona as fio
import shapely as shp
import numpy as np
import os
from buhayra.getpaths import *
from buhayra.utils import getWMinScene, raster2rect, geojson2shapely
import shapely
import matplotlib.pyplot as plt


tifsdir='/home/delgado/dem_mount'
tifs=os.listdir(tifsdir)
tifsF=list()
for tif in tifs:
    if tif.endswith('F.tif'):
        tifsF.append(tif)

rasterF=tifsF[0]

wm=fio.open(home['proj']+'/buhayra/auxdata/wm_utm_'+location['postgis_db']+'.gpkg','r')

with fio.open(home['proj']+'/buhayra/auxdata/wm_utm_'+location['postgis_db']+'.gpkg','r') as wm:
    for rasterF in tifsF:
        raster = rio.open(os.path.join(tifsdir,rasterF))
        for pol in wm.filter(bbox=raster.bounds):
            feat=geojson2shapely(pol['geometry'])
            pol['geometry']=feat.buffer(60) # one pixel is 30x30
            out_image, out_transform = rasterio.mask.mask(raster,
                [pol['geometry']],
                crop=True,
                nodata=-9999)
            if np.max(out_image) ==-9999.0:
                continue
            out_meta = raster.meta.copy()
            out_meta.update({"driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform})
            with rio.open("{}_masked.tif".
                  format(pol['id']),
                  "w",
                  **out_meta) as dest:
                dest.write(out_image)
            break


        out_image
        mask=np.ma.array(out_image[0]==-9999)
        r=np.ma.array(out_image[0],mask=mask)
        i=11
        for i in range(20):
            lower=np.percentile(r.compressed(),i*5)
            upper=np.percentile(r.compressed(),(1+i)*5)

            b = np.where((r > lower) & (r <= upper), True, False)
            np.count_nonzero(b[0])
