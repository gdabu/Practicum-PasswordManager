import logging

def initLogger(logPath):

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # create a file handler

    handler = logging.FileHandler(logPath)
    handler.setLevel(logging.INFO)

    # create a logging format

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    
    logger.addHandler(handler)

    return logger