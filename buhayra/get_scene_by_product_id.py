from sentinelsat import SentinelAPI
from buhayra.getpaths import *

product_id='S1A_IW_GRDH_1SDV_20190815T081736_20190815T081801_028577_033B6C_8DFC'

api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')

is_online = api.is_online(product_id)
if is_online:
    print('Product {} is online. Starting download.'.format(product_id))
    api.download(product_id)
else:
    print('Product {} is not online.'.format(product_id))
