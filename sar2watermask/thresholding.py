from buhayra.getpaths import *
from os import listdir
import numpy as np
import numpy.ma as ma
import rasterio
from rasterio.features import shapes
import matplotlib.pyplot as plt
import time
import shapely
import shapely.geometry


wm=apply_thresh()
plt.imshow(wm)


import copy
r=copy.deepcopy(wm)

## this fills the whole raster:
r.fill(1) # not useful

rshape=(r.mask*-1+1)*r.data
plt.imshow(rshape)
rshape.dtype='int32'

lsh=list(shapes(rshape))
lsh
shapely.geometry.shape(lsh[0][0])

np.amax(r)


np.amax(r.mask)

plt.imshow(r)

list(shapes(wm))
### polygonize, calc area and clean small features





def selectTiff():
    if(len(listdir(sarOut))<1):
        logger.info(sarOut+" is empty! Nothing to do. Exiting and returning None.")
        return None
    l=listdir(sarOut)
    import re
    for s in l:
        if re.search('.tif$',s):
            return(s)
    return(s)



def apply_thresh():
    f=selectTiff()
    with rasterio.open(sarOut+'/'+f,'r+') as ds:
        r=ds.read(1)

        rmsk=ma.array(r,mask= (r==0))

        thr=kittler(rmsk)

        while(thr>60000):
            thr=kittler(ma.array(r,mask= (rmsk>thr)))
            if(thr is None):
                break

        if(thr<40000):
            wm=ma.array(r,mask= ((r>=thr) | (r==0)))
            wm.fill(1) # not useful
            rshape=(wm.mask*-1+1)*wm.data
            rshape.dtype='int32'
            ds.write(rshape,1)
            ds.close()


def kittler(nparray):
    """
    Calculates minimum threshold
    nparray: numpy array
    return: threshold
    """
    # get indices of missing values
    # and mask them

    n = np.isnan(nparray)
    band = np.ma.masked_array(nparray, mask=n)


    # count entries in array
    if band.count() < 50:
        print("The size of the population is smaller than 50!\n")
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
