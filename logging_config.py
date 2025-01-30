import logging

class CustomFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if record.levelno == logging.INFO:
            color = f'\033[34m{levelname}\033[0m'
        elif record.levelno == logging.ERROR:
            color = f'\033[31m{levelname}\033[0m'
        elif record.levelno == logging.WARN:
            color = f'\033[33m{levelname}\033[0m'
        else:
            color = levelname
        record.levelname = color
        return super().format(record)

def configure_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    for handler in logger.handlers:
        handler.setFormatter(CustomFormatter('[\033[34m%(asctime)s\033[0m] [%(levelname)s] %(message)s'))
        handler.formatter.datefmt = "%H:%M:%S"
    return logger