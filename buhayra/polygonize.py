import os
from buhayra.getpaths import *
import buhayra.utils as utils
import logging
import rasterio
from rasterio import features
import shapely
from shapely.geometry import mapping, Polygon, shape
from shapely.ops import cascaded_union, transform
import fiona
import datetime
import json
import numpy as np
import geojson

# for edge detection
import rasterio.mask
from skimage import feature
from skimage.morphology import skeletonize
import cv2


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

def load_metadata(f):
    with open(polOut+'/'+f[:-3]+'json', 'r') as fjson:
        metadata = json.load(fjson)
    return metadata

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


def select_intersecting_polys(geom,refgeoms,f):
    metalist=f[:-4].split('_')

    geom=utils.wgs2utm(geom.buffer(0))

    refgeom = refgeoms[int(metalist[9])]

    inters=list()
    if geom.geom_type == 'MultiPolygon':
        for poly in geom:
            if poly.intersects(refgeom):
                inters.append(poly)
        if len(inters)>0:
            geom_out = cascaded_union(inters)
            # s=json.dumps(mapping(inters))
            # feat['geometry']=json.loads(s)
        else:
            geom_out=Polygon().buffer(0)
    elif geom.geom_type == 'Polygon':
        if geom.intersects(refgeom):
            geom_out=geom
            # s=json.dumps(mapping(geom))
            # feat['geometry']=json.loads(s)
        else:
            geom_out=Polygon().buffer(0)

    xgeom = refgeom.intersection(geom_out)

    return geom_out, xgeom.area

def prepareDict(poly,f,thr,intersection_area):
    metalist=f[:-4].split('_')
    sentx=metalist[0]
    if np.isnan(thr):
        thr=0
    props={
        'source_id':sentx,
        'ingestion_time':datetime.datetime.strptime(metalist[4],'%Y%m%dT%H%M%S'),
        'id_jrc':int(metalist[9]),
        'threshold':thr,
        'wmXjrc_area':intersection_area,}

    poly_wgs=utils.utm2wgs(poly.buffer(0))

    s=json.dumps(mapping(poly_wgs))
    geom=json.loads(s)


    feat={
        'type':'Feature',
        'properties':props,
        'geometry':geom
        }
    feat['properties']['area']=poly.area

    return feat


def json2geojson(ls):
    logger = logging.getLogger('root')
    feats=[]
    for dict in ls:
        if type(dict['properties']['ingestion_time']) == datetime.datetime:
            dttm=dict['properties']['ingestion_time']
            dttmstr=dttm.strftime("%Y-%m-%d %H:%M:%S")
            dict['properties']['ingestion_time']=dttmstr

        if dict['geometry'] is None or len(dict['geometry']['coordinates'])==0:
            feats.append(geojson.Feature(geometry=None,properties=dict['properties']))
        else:
            ## mixing poly and multipoly is not accepted by postgis. we will force Polygon into MultiPolygon
            mp=geojson.MultiPolygon()

            ## now we have to correct syntax of MultiPolygon which was forced from Polygon so it generates valid geojson in the end
            if dict["geometry"]["type"]=='Polygon':
                dict["geometry"]["coordinates"]=[dict["geometry"]["coordinates"]]
            #if len(poly['geometry']['coordinates'])==1:
            #    mp=geojson.Polygon()

            mp['coordinates']=dict['geometry']['coordinates']
            feats.append(geojson.Feature(geometry=mp,properties=dict['properties']))



    return geojson.FeatureCollection(feats)
