# connect to the API
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date, datetime, timedelta
import sys
import os
from buhayra.getpaths import *
import logging
from bs4 import BeautifulSoup
import requests
import urllib
from buhayra.location import *
import time

logging.basicConfig(format='%(message)s', level='INFO')

def main():

    if len(sys.argv) < 2:
        print("  Usage: python3 get_past_scenes.py [year] [month]")
        return 1
    api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')

    logging.info(api.api_url)

    t0 = datetime(int(sys.argv[1]),int(sys.argv[2]),1,0,0,0)
    tf = t0 + timedelta(days=12)

    # search by polygon, time, and SciHub query keywords
    footprint = geojson_to_wkt(read_geojson(home['parameters'] + '/extent_'+location['region']+'.geojson'))

    products_s1a = api.query(footprint,
                         date=(
                             date(t0.year,t0.month,t0.day),
                             date(tf.year,tf.month,tf.day)
                         ),
                         producttype="GRD",
                         platformname='Sentinel-1')

    unavailable=[]
    for uuid in products_s1a:
        product_info = api.get_product_odata(uuid)
        if any(product_info['title'] in s for s in os.listdir(sarIn)):
            logging.info('Skipping '+uuid+'. Already exists in '+sarIn)
            continue
        logging.info('Is ' + uuid +' online?')
        logging.info(product_info['Online'])
        if not product_info['Online']:
            logging.info('Requesting unavailable uuids')
            api.download(uuid)
            unavailable=unavailable + [uuid]
        else:
            logging.info('Downloading available uuids')
            api.download(uuid,directory_path=sarIn)
        logging.info('Sleeping 30 minutes (the API does not allow intensive requests)')
        time.sleep(30*60)


    while len(unavailable)>0:
        for uuid in unavailable:
            product_info = api.get_product_odata(uuid)
            if product_info['Online']:
                logging.info(uuid + ' is available! Downloading:')
                api.download(uuid,directory_path=sarIn)
                unavailable.remove(uuid)
        time.sleep(600)
    return 0

if __name__ == "__main__":
    main()
