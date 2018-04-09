import os
import time
from modules.getPaths import *

current_time = time.time()

for f in os.listdir(sarOut):
    creation_time = os.path.getctime(sarOut + "/" + f)
    if (current_time - creation_time) // (24 * 3600) >= 14:
        os.unlink(sarOut + "/" +f)
        print('{} removed'.format(f))

for f in os.listdir(sarIn):
    creation_time = os.path.getctime(sarIn + "/" +f)
    if (current_time - creation_time) // (24 * 3600) >= 14:
        os.unlink(sarIn + "/" + f)
        print('{} removed'.format(f))

for f in os.listdir(polOut):
    creation_time = os.path.getctime(polOut + "/" + f)
    if (current_time - creation_time) // (24 * 3600) >= 14:
        os.unlink(polOut + "/" +f)
        print('{} removed'.format(f))
