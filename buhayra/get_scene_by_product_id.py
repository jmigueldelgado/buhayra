from sentinelsat import SentinelAPI
from buhayra.getpaths import *

product_id='12c35311-1184-4147-86fa-5fc5404cc102'

api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')

is_online = api.is_online(product_id)
if is_online:
    print('Product {} is online. Starting download.'.format(product_id))
    api.download(product_id)
else:
    print('Product {} is not online.'.format(product_id))
