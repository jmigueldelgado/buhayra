import os
import subprocess
import glob
import datetime
from modules.getPaths import *

t0=datetime.datetime.now()

print("First polygonize SAR\n")

items=os.listdir(sarOut)
newlist = []
for names in items:
    if names.endswith("watermask.tif"):
        newlist.append(names[:-4])

#newlist = list(set(newlist))
#newlist
#scene=newlist[0]

for scene in newlist:

    print("\n polygonizing " + scene + "\n")
    out_gml = scene + ".gml"
    subprocess.call([pyt,gdalPol,sarOut + "/" + scene + ".tif","-f","GML",polOut + "/" + out_gml])
    os.remove(sarOut + "/" + scene + ".tif")

print("\n********** sentinel-1 polygonize completed!" + str(len(newlist))  + " watermasks processed\n********** Elapsed time: " + str(datetime.datetime.now()-t0) + "\n********** End of message\n")




####################################################################################
######### polygonize S2A


print("... now polygonize S2A\n")

items=os.listdir(s2aOut)
newlist = []
for names in items:
    if names.endswith("watermask.tif"):
        newlist.append(names[:-4])

newlist = list(set(newlist))
#print(newlist)


for scene in newlist:
    print("\n polygonizing " + scene + "\n")
    out_gml = scene + ".gml"
    subprocess.call([pyt,gdalPol,s2aOut + "/" + scene + ".tif","-f","GML",polOut + "/" + out_gml])
    os.remove(s2aOut + "/" + scene + ".tif")

print("\n********** sentinel-2 polygonize completed!" + str(len(newlist))  + " watermasks processed\n********** Elapsed time: " + str(datetime.datetime.now()-t0) + "\n********** End of message\n")
