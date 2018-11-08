from buhayra.getpaths import *
import numpy as np
import numpy.ma as ma
import rasterio
import logging
import os
import json
from shutil import copyfile
# f=selectTiff(sarOut)
#
# apply_thresh(f) ## applies threshold to tiff in scratch

def thresholdLoop():
    logger = logging.getLogger('root')
    while(selectTiff(sarOut)):
        f=selectTiff(sarOut)
        thr=apply_thresh(f)
        if thr is None:
            logger.debug('moving away '+f)
            os.rename(sarOut+'/'+f,procOut+'/'+f)
            os.rename(sarOut+'/'+f[:-3]+'json',procOut+'/'+f[:-3]+'json')
        else:
            logger.debug('moving away '+f+'')
            os.rename(sarOut+'/'+f,procOut+'/'+f)
            os.rename(sarOut+'/'+f[:-3]+'json',procOut+'/'+f[:-3]+'json')
            logger.debug('Threshold for '+f + ' is ' + str(thr))

def apply_thresh(f):
    with rasterio.open(sarOut+'/'+f,'r') as ds:
        r=ds.read(1)
        # gdalParam=ds.transform.to_gdal()

        rmsk=ma.array(r,mask= (r==0))
        thr=kittler(rmsk)
        if thr is None:
            return None

        while(thr>60000):
            thr=kittler(ma.array(r,mask= (rmsk>thr)))
            if thr is None:
                return None

        wm=ma.array(r,mask= ((r>=thr) | (r==0)))
        wm.fill(1)
        if(thr<40000):
            rshape=(wm.mask*-1+1)*wm.data
        else:
            return None
        with rasterio.open(polOut+'/'+f,'w',driver=ds.driver,height=ds.height,width=ds.width,count=1,dtype=rasterio.uint8) as dsout:
            dsout.write(rshape.astype(rasterio.uint8),1)

    copyfile(sarOut+'/'+f[:-3]+'json',polOut+'/'+f[:-3]+'json')
    return(thr)

def kittler(nparray):
    """
    Calculates minimum threshold
    nparray: numpy array
    return: threshold
    """
    # get indices of missing values
    # and mask them
    logger = logging.getLogger('root')

    n = np.isnan(nparray)
    band = np.ma.masked_array(nparray, mask=n)


    # count entries in array
    if band.count() < 50:
        logger.info("The size of the population is smaller than 50! Returning None")
        return None
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
