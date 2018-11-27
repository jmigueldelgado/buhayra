from buhayra.thresholding import *

scenes=select_n_last_tiffs(1)
f=scenes[0]

f
ds=rasterio.open(sarOut+'/'+f,'r')
rect_utm=getBoundingBoxScene(ds)
wm_in_scene,id_in_scene = getWMinScene(rect_utm)
i=5000
fname=f[:-4] + "_" + str(id_in_scene[i])+".tif"
out_image,out_transform=subset_by_lake(ds,wm_in_scene[i])
gdalParam=out_transform.to_gdal()
r_db=sigma_naught(out_image[0])

splt=subset_200x200(r_db)

thr=list()


for i in range(len(splt)):
    thr_i=list()
    # subres=list()
    for j in range(len(splt[i])):
        thr_i.append(get_thr(splt[i][j])) # subres.append(threshold(splt[i][j]))
    # res.append(subres)
    thr.append(thr_i)

# thr_i=[1,2,3,np.nan]
# thr=list()
# thr.append(thr_i)
# thr
npthr = np.array(thr)
thrmedian=np.nanmedian(npthr)

nparray=r_db
thr=thrmedian

n = nparray==np.iinfo(nparray.dtype).min
band = ma.masked_array(nparray, mask=n,fill_value=0)

if np.isnan(thr):
    band[:]=ma.masked
elif(np.amax(nparray)< -1300): # all cells in raster are open water
    band.data.fill(1)
elif(thr < -1300):          # there is a threshold and it is a valid threshold
    band[band>thr]=ma.masked
    band.data.fill(1)
else: # the threshold is too large to be a valid threshold
    band[:]=ma.masked

band.data[band.mask]=0
openwater=band.data

openwater=threshold(r_db,thrmedian)

with rasterio.open(polOut+'/'+fname,'w',driver=ds.driver,height=openwater.shape[0],width=openwater.shape[1],count=1,dtype=rasterio.ubyte) as dsout:
    dsout.write(openwater.astype(rasterio.ubyte),1)





####################################
####################################
####################################

from buhayra.thresholding import *


f=select_n_last_tiffs(1)[0]

ds=rasterio.open(sarOut+'/'+f,'r')        # ds=rasterio.open('/home/delgado/Documents/tmp/testproduct_watermask.tif')
        # r=ds.read(1)

rect_utm=getBoundingBoxScene(ds)
wm_in_scene,id_in_scene = getWMinScene(rect_utm)


len(wm_in_scene)

user_thresh=-1000
i=3

fname=f[:-4] + "_" + str(id_in_scene[i])+".tif"
out_image,out_transform=subset_by_lake(ds,wm_in_scene[i])
gdalParam=out_transform.to_gdal()
out_db=sigma_naught(out_image[0])


openwater,thr=apply_thresh(out_db)
gdalParam=list(gdalParam)
gdalParam.append(thr)


with rasterio.open(polOut+'/'+fname,'w',driver=ds.driver,height=openwater.shape[0],width=openwater.shape[1],count=1,dtype=rasterio.ubyte,transform=out_transform,crs=ds.crs) as dsout:
    dsout.write(openwater.astype(rasterio.ubyte),1)
