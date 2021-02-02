
# for edge detection
import logging
import rasterio
import rasterio.mask
from rasterio import features
from skimage import feature
from skimage.morphology import skeletonize
import cv2
import os
import numpy as np


def load_watermask(f):
    with rasterio.open(polOut+'/'+f,'r') as ds:
        ds.profile.update(dtype=rasterio.int32)
        r=ds.read(1)
    return r

def raster2shapely(r,metadata):
    affParam=rasterio.Affine.from_gdal(metadata[0],metadata[1],metadata[2],metadata[3],metadata[4],metadata[5])
    polys=list()
    for pol, value in features.shapes(r, transform=affParam):
        if value==1:
            polys.append(shape(pol))
    return cascaded_union(polys)

def edge_classification(tif_filename):
    productName='_'.join(tif_filename[:-4].split('_')[:9])

    # open radar data after speckle filtering and geometric correction etc (see buhayra)
    with rasterio.open(os.path.join(sarOut,productName,tif_filename),'r') as ds:
        im=ds.read(1)

    if im.max()<-1000000:
        return -1

    # standardize data ("feature scaling", "z-score normalization")
    im=(im-np.mean(im))/np.std(im)

    # plt.imshow(im)

    # apply canny edge detection with very conservative low and high threshold
    edges1 = feature.canny(im,sigma=2,low_threshold=0.8,high_threshold=1)
    # plt.imshow(edges1)

    # Open metadata (affine parameters) and save projected edges
    with open(os.path.join(sarOut,productName,tif_filename[:-3]+'json'), 'r') as fjson:
        metadata = json.load(fjson)

    affParam=rasterio.Affine.from_gdal(metadata[0],metadata[1],metadata[2],metadata[3],metadata[4],metadata[5])
    projected_edges = rasterio.open(os.path.join(edgeOut,productName,tif_filename[:-4] + '_projected_edges.tif'), 'w', driver='GTiff',
                                height = edges1.shape[0], width = edges1.shape[1],
                                count=1, dtype=edges1.astype(rasterio.int16).dtype,
                                crs='+proj=latlong',
                                transform=affParam)
    projected_edges.write(edges1.astype(rasterio.int16),1)
    projected_edges.close()
    id=int(tif_filename[:-4].split('_')[9])
    return id



# refgeom is a shapely polygon. crs_transform is of class pyproj.Transformer.from_crs
def morphological_transformations(tif_filename,refgeom,crs_transform):
    id=tif_filename[:-4].split('_')[9]
    productName='_'.join(tif_filename[:-4].split('_')[:9])

    # Buffer/dilate maximum extent of reservoir polygon for masking by 0.5*sqrt(A/pi).
    # Reproject in UTM.
    wgs_shape = transform(crs_transform, refgeom.buffer(0.5*(refgeom.area/3.14)**0.5))

    # Mask edge raster with dilated shape
    with rasterio.open(os.path.join(edgeOut,productName,tif_filename[:-4] + '_projected_edges.tif'),'r') as src:
        out_image, out_transform = rasterio.mask.mask(src, [wgs_shape], crop=True)
        out_meta = src.meta

    ## Morphlogical Transformations to the edge raster: create kernel, dilate edges, skeletonize
    ## kernel is a circle of diameter 3
    ## dilate edges to bridge spurious discontinuities in edge
    ## skeletonize to restore linear edges

    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    dilated = cv2.dilate(out_image[0],kernel)
    skeleton = skeletonize(dilated).astype(rasterio.int16)
    return skeleton, out_transform


def save_edge_coordinates(skeleton,tif_filename,out_transform):
    ## Obtain coordinates of each raster cell that was classified as an edge
    productName='_'.join(tif_filename[:-4].split('_')[:9])

    pts=list()
    snake_i=0
    for pol, value in rasterio.features.shapes(skeleton, connectivity=8, transform=out_transform):
        if value == 1:
            ij=np.where(1 == rasterio.features.rasterize((pol,1),fill=0,out=np.zeros(skeleton.shape),transform=out_transform,all_touched=False))
            if len([ii for ii,jj in zip(*ij)])>=10: # we need at least 4 points to draw a polygon so it is better to have much more points to draw a concave hull around the feature
                for ii,jj in zip(*ij):
                    pts.append([snake_i] + list(rasterio.transform.xy(out_transform,ii,jj)))
            snake_i=snake_i+1

    # Save coordinates as a geospatial dataframe
    import pandas as pd
    import geopandas as gpd

    df = pd.DataFrame({'id':[line[0] for line in pts],'x':[line[1] for line in pts],'y':[line[2] for line in pts]})

    if len(df.index)<=10:
        open(os.path.join(edgeOut,productName,tif_filename[:-4]+'_empty_geometry.geojson'),'w').close()
        return -1
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.x,df.y))

    # Export as geojson
    gdf.to_file(os.path.join(edgeOut,productName,tif_filename[:-3]+'geojson'),driver='GeoJSON')
    return os.path.join(edgeOut,productName,tif_filename[:-3]+'geojson')
