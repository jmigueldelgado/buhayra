import logging
from pymongo import MongoClient
import os
import sys
from datetime import datetime
import logging
from buhayra.getpaths import *
from buhayra.credentials import *

def testMongoConnect():

    client = MongoClient('mongodb://'+ MONGO_USER + ':' + MONGO_PASS + '@' + MONGO_HOST + '/' + MONGO_DB)

    db = client.sar2watermask
    neb = db.neb ##  collection
    print(db.collection_names())

def test_logging():
    # print("testing logging")
    logger = logging.getLogger('root')
    # logger.addHandler(handler)

    a='abc'
    #print(a+'\n')
    logger.debug('My message with %s', a)
    logger.info('Logging is working')
