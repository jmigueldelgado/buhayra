import logging

def testing_logging():
    # print("testing logging")
    logger = logging.getLogger('root')
    # logger.addHandler(handler)

    a='abc'
    #print(a+'\n')
    logger.debug('My message with %s', a)
    logger.info('Logging is working')
