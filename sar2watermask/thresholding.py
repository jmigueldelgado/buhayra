import rasterio
from buhayra.getpaths import *
from os import listdir

f=selectTiff()
dataset = rasterio.open(f)



def selectTiff():
    if(len(listdir(sarOut))<1):
        logger.info(sarOut+" is empty! Nothing to do. Exiting and returning None.")
        return None
    l=listdir(sarOut)
    import re
    s=l[1]
    for s in l:
        match=re.search('.tif',s)
        match

    f=listdir(sarOut)[0]
    return(f)
