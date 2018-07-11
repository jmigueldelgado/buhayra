import logging

def testing_logging():
    logger = logging.getLogger(__name__)
    a='abc'
    #print(a+'\n')
    logger.debug('My message with %s', a)
    logger.info('Logging is working')
