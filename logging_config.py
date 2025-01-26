import logging
from logging.handlers import RotatingFileHandler

def configure_logging():
    logger = logging.getLogger("MilitaryApp")
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler("military_app.log", maxBytes=5*1024*1024, backupCount=3)  
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = configure_logging()