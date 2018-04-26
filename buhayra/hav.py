import rasterio as rio
import fiona as fio
import fiona.transform
import rasterio.mask
from matplotlib.pyplot import imshow



fname="/home/delgado/SESAM/sesam_data/DFG_Erkenntnis_Transfer/tdx/DEMs/dfd2_506518124_sum_dem_20151014_4x4_geoc_F.tif"
dataset = rio.open(fname)
#dem = dataset.read(1)

##### with shapely
m="/home/delgado/Documents/S1A_IW_GRDH_1SDV_20180422T081723_20180422T081748_021577_0252FF_65E0_x1000_y0_watermask_simplified.geojson"
MASKS=fio.open(m)

newMASKS=list()
for geom in MASKS:
    newgeom=geom
    newgeom['geometry']=fiona.transform.transform_geom(MASKS.crs['init'],dataset.crs['init'],geom['geometry'])
    newMASKS.append(newgeom)


band.max()
band.min()
band[band<300]=300

band, out_transform =rio.mask.mask(dataset,newMASKS,all_touched=True) ### the mask has to be a list of geojson!

list()

band
