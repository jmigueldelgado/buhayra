import os
from buhayra.getpaths import *
import logging
import requests
from buhayra.location import *
import buhayra.log as log
from urllib.parse import urlparse
import time
from bs4 import BeautifulSoup
from datetime import date
from datetime import timedelta
import re
logger = log.setup_custom_logger('root','INFO')
url=imerg_home

ext='nc4'
def get_url_paths(url, ext='', params={}):
    """Lists URL paths to files with a given extention
    :param url: URL to the parent path
    :param ext: Local file name to contain the data downloaded
    :param params: parameters to pass to requests.get (optional)
    :return: parent_contents an array of strings with file names present in parent url
    """
    response = requests.get(url, params=params)
    if response.ok:
        response_text = response.text
    else:
        return response.raise_for_status()
    soup = BeautifulSoup(response_text, 'html.parser')
    parent_contents = [url + '/' + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
    return parent_contents


def download_from_url(url: str, file_path='', attempts=28):
    """Downloads a URL content into a file (with large file support by streaming)

    :param url: URL to download
    :param file_path: Local file name to contain the data downloaded
    :param attempts: Number of attempts
    :return: New file path. Empty string if the download failed
    """
    logger.info("Checking if path is correct and file already exists.")
    logger.info(url)
    if not file_path:
        file_path = os.path.realpath(os.path.basename(url))
    logger.info(f'Downloading {url} content to {file_path}')
    if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
        logger.info("File already exists and is readable. Not downloading again.")
        return None
    else:
        logger.info("File either inexistant or unreadable. Downloading.")
    url_sections = urlparse(url)
    if not url_sections.scheme:
        logger.info('The given url is missing a scheme. Adding http scheme')
        url = f'http://{url}'
        logger.info(f'New url: {url}')
    for attempt in range(1, attempts+1):
        try:
            if attempt > 1:
                time.sleep(60*6)  # 10 seconds wait time between downloads    with requests.get(url, stream=True) as r:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info('Download finished successfully')
                return True
        except Exception as ex:
            logger.error(f'Attempt #{attempt} of {attempts} failed with error: {ex}')

ref_date=date.today()-timedelta(days=2)
ref_strg='{:4d}'.format(ref_date.year)+'{:02d}'.format(ref_date.month)+'{:02d}'.format(ref_date.day)
imerg_home='https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGDE.06/' + '{:4d}'.format(ref_date.year) + '/' + '{:02d}'.format(ref_date.month)
imerg_url=imerg_home + '3B-DAY-E.MS.MRG.3IMERG.'+ ref_strg + '-S000000-E235959.V06.nc4'
download_from_url(imerg_url,file_path=home['scratch']+'/imerg/'+imerg_url.split('/')[-1])
