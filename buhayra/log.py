import logging
import os

pid=os.getpid()

def setup_custom_logger(name,level="INFO"):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.FileHandler('info' + str(pid) + '.log')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    if level=="DEBUG":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.addHandler(handler)
    return logger
