### load dataset
import rasterio as rio
import matplotlib.pyplot as plt
import numpy as np
import subprocess
from skimage.filters import threshold_otsu, threshold_local

dataset = rio.open('/home/delgado/proj/sar2watermask/s1a_scenes/out/S1A_IW_GRDH_1SDV_20171105T081725_20171105T081750_019127_0205D1_D44E_x500_y0_TC.tif')
image = dataset.read(1)

profile=dataset.profile
profile.update(dtype=rio.uint8,count=1)

img = image/image.max()

scene = image>0.000
bdr = image == 0.


#### manual threshold

manual = image < 0.02
manual[bdr] = False

plt.imshow(manual)

fileName='example-global_manual'

with rio.open(fileName+'.tif', 'w', **profile) as dst:
    dst.write(manual.astype(rio.uint8), 1)



#### single out land

#### first define a mask with pixels that are for sure land
threshold_global_otsu = threshold_otsu(img[scene])

binary_global = img > threshold_global_otsu
land = binary_global

######  true is yellow

plt.imshow(binary_global)

notland = land != True
notland[bdr] = False

threshold_global_otsu = threshold_otsu(img[notland])


binary_global2 = img < threshold_global_otsu

binary_global2[bdr] = False

img[binary_global2].max()

plt.imshow(binary_global2)

fileName='example-global_otsu'

with rio.open(fileName+'.tif', 'w', **profile) as dst:
    dst.write(binary_global.astype(rio.uint8), 1)




from skimage.morphology import disk
from skimage.filters import rank

radius = 15
selem = disk(radius)

threshold_local_otsu = rank.otsu(img, selem)

binary_local = img > threshold_local_otsu

plt.imshow(binary_local)

fileName='example-local_otsu'

with rio.open(fileName+'.tif', 'w', **profile) as dst:
    dst.write(binary_local.astype(rio.uint8), 1)
#subprocess.call(["python","/home/delgado/local/miniconda2/envs/image/bin/gdal_polygonize.py",fileName + '.tif',"-f","GML",fileName + ".gml"])
