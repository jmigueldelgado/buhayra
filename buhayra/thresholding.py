import datetime
from buhayra.getpaths import *
import numpy as np
import numpy.ma as ma
import rasterio
import rasterio.mask
import fiona
import logging
import os
import json
from shutil import copyfile
from shapely.geometry import Polygon, shape
import pyproj
from functools import partial
from shapely.ops import transform
from dask import compute, delayed
import dask.multiprocessing


def threshold_loop(tiffs):
    logger = logging.getLogger('root')
    values = [delayed(process)(f) for f in tiffs]
    results = compute(*values, scheduler='processes')
    logger.info('finished threshold loop. processed '+str(len(tiffs)) + ' tifs')

def process(f):
    with rasterio.open(sarOut+'/'+f,'r') as ds:
        if (f) in listdir(polOut):
            logger.info("product "+f+" already exists: skipping")
            return None

        gdalParam=ds.transform.to_gdal()

        r=ds.read(1)
        out_db=scale_integer(r)

        logger.debug("saving compressed version of lake subset")
        with rasterio.open(procOut+'/'+f,'w',driver=ds.driver,height=out_db.shape[0],width=out_db.shape[1],count=1,dtype=out_db.dtype) as dsout:
            dsout.write(out_db,1)

        openwater,thr=apply_thresh(out_db)
        gdalParam=list(gdalParam)
        gdalParam.append(thr)
        logger.debug("saving metadata of lake subset, including determined threshold")
        with open(procOut+'/'+fname[:-3]+'json', 'w') as fjson:
            json.dump(gdalParam, fjson)


        if not np.isnan(thr):
            logger.debug("writing out to sarOut "+fname)

            with rasterio.open(polOut+'/'+fname,'w',driver=ds.driver,height=openwater.shape[0],width=openwater.shape[1],count=1,dtype=rasterio.ubyte,transform=ds.transform) as dsout:
                dsout.write(openwater.astype(rasterio.ubyte),1)
            with open(polOut+'/'+fname[:-3]+'json', 'w') as fjson:
                json.dump(gdalParam, fjson)

        logger.debug('removing '+f)
        os.remove(sarOut+'/'+f)
        os.remove(sarOut+'/'+f[:-3]+'xml')
        return f


def apply_thresh(r_db):
    # subset into 200x200 m approx.
    splt=subset_200x200(r_db)

    ### loop through subsets
    # res=list()
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

    openwater=threshold(r_db,thrmedian)
    # ### stitch raster back together
    # for i in range(len(res)):
    #     res[i]=np.concatenate(res[i],1)
    # openwater=np.concatenate(res,0)

    return(openwater,thrmedian)

def subset_200x200(nparray):

    splt=list()
    if nparray.shape[0]>0 and nparray.shape[1]>0:
        n=np.ceil(nparray.shape[0]/20)
        splt0=np.array_split(nparray,n,0)
        for chunk in splt0:
            m=np.ceil(chunk.shape[1]/20)
            splt1=np.array_split(chunk,m,1)
            splt.append(splt1)
        return(splt)

def threshold(nparray,thr):
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

    return(band.data)

def get_thr(nparray):
    logger = logging.getLogger('root')
    try:
        thr=kittler(nparray)
    except:
        e = sys.exc_info()[0]
        logger.info( "Error in kittler: %s" % e )
        thr=np.nan # there was an error computing the threshold, check the error message
    if(thr > -1300): # threshold is too large to be a valid water-land threshold
        thr=np.nan
    if(np.amax(nparray)< -1300): # all cells in raster are open water
        thr=np.nan
    return(thr)

def kittler(nparray):
    """
    Calculates minimum threshold
    nparray: numpy array
    return: threshold
    """
    logger = logging.getLogger('root')

    # get indices of missing values
    # missing value is np.iinfo(np.int16).min or np.iinfo(np.int32).min depending on dtype
    # and mask them

    try:
        n = nparray==np.iinfo(nparray.dtype).min
        band = ma.masked_array(nparray, mask=n)
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        logger.info(nparray.dtype)
        logger.info( "Error: %s" % e )
        return(None)


    # count entries in array
    if band.count() < 50:
        logger.debug("The size of the population is smaller than 50! Returning None")
        return np.nan
    else:
        # calculate minimum and maximum as histogram breaks
        breaks = [band.min(), np.ceil(band.max()) + 1]
        # create sequence of min and max, determine length(=number of bins)
        breaksSeq = np.arange(breaks[0], breaks[1], 5)

        b = (breaksSeq[0], breaksSeq[-1])
        bins = len(breaksSeq) - 1
        # get density of each bin
        density = np.histogram(band, bins=bins, range=b, density=True)[0]
        g=np.arange(1,bins+1)
        gg = [i**2 for i in g]

        C = np.cumsum(density)
        M = np.cumsum(density * g)
        S = np.cumsum(density * gg)
        sigmaF = np.sqrt(S / C - (M / C) ** 2)


        Cb = C[len(g) - 1] - C
        Mb = M[len(g) - 1] - M
        Sb = S[len(g) - 1] - S
        sigmaB = np.sqrt(np.abs(Sb / Cb - (Mb / Cb) ** 2))

        P = C / C[len(g) - 1]

        V = P * np.log(sigmaF) + (1 - P) * np.log(sigmaB) - P * np.log(P) - (1 - P) * np.log(1 - P)
        V[np.isinf(V)] = np.nan

        minV = np.nanmin(V)
        for m in range(len(g)):
            if V[m] == minV:
                threshold = breaksSeq[m]

        return threshold

def select_tiffs_year_month(Y,M):
    logger = logging.getLogger('root')

    if(len(listdir(sarOut))<1):
        logger.info(sarOut+" is empty! Nothing to do. Exiting and returning None.")
        tiffs_in_ym=None
    else:
        timestamp=list()
        tiffs_in_ym=list()
        for tif in listdir(sarOut):
            if not tif.startswith('S'):
                continue
            stamp=datetime.datetime.strptime(tif.split('_')[4],'%Y%m%dT%H%M%S')
            if re.search('.tif$',tif) and stamp.year==Y and stamp.month==M:
                tiffs_in_ym.append(tif)
                timestamp.append(stamp)
        if(len(timestamp)<1):
            logger.info(sarOut+" has no tiffs for year "+Y+" and month "+M+"Exiting and returning None.")
            tiffs_in_ym=None
    return(tiffs_in_ym)

def select_n_last_tiffs(n):
    logger = logging.getLogger('root')

    if(len(listdir(sarOut))<1):
        logger.info(sarOut+" is empty! Nothing to do. Exiting and returning None.")
        tiffs=None
    else:
        timestamp=list()
        tiffs=list()
        for tiff in listdir(sarOut):
            stamp=datetime.datetime.strptime(tiff.split('_')[4],'%Y%m%dT%H%M%S')
            if re.search('.tif$',tiff):
                tiffs.append(tiff)
                timestamp.append(stamp)

        if(len(timestamp)<1):
            logger.info(sarOut+"Has not tifs. Exiting and returning None.")
            tiffs.append(None)
        if(len(timestamp)<=n):
            return(tiffs)
        else:
            index=np.argsort(timestamp)
            return([tiffs[i] for i in index[-n:]])
    return(tiffs)


def scale_integer(r_db):
    r_db[r_db==-999999999]=np.nan

    if (np.nanmax(r_db)< np.iinfo(np.int16).max) and (np.nanmin(r_db) > (np.iinfo(np.int16).min+1)):
        r_db[np.isnan(r_db)]=np.iinfo(np.int16).min
        r_db=np.int16(r_db)
    else:
        r_db[np.isnan(r_db)]=np.iinfo(np.int32).min
        r_db=np.int32(r_db)
    return(r_db)

def checknclean(pol):
    if not pol.is_valid:
        clean=pol.buffer(0)
        return(clean)
    else:
        return(pol)
