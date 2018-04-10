#! /usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Calculates minimum threshold 
from rasterio image

    Usage:
        kittler.py <image>

    Arguments:
        image       image file

"""

from docopt import docopt
import numpy as np
import rasterio


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
        print "The size of the population is smaller than 50!\n"
    else:
        # calculate minimum and maximum as histogram breaks
        breaks = [band.min(), np.ceil(band.max()) + 1]
        # create sequence of min and max, determine length(=number of bins)
        breaksSeq = np.arange(breaks[0], breaks[1], 1)
        b = (breaksSeq[0], breaksSeq[-1])
        bins = len(breaksSeq) - 1
        # get density of each bin
        density = np.histogram(band, bins=bins, range=b, density=True)[0]
        g = range(1, int(np.ceil(band.max() + 1)))
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


if __name__ == '__main__':
    args = docopt(__doc__)
    i = args['<image>']

    # read file and get band data as numpy array
    dataset = rasterio.open(i)
    band1 = dataset.read(1)

    t = kittler(band1)
    print t

    


