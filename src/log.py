from logging import getLogger, StreamHandler, FileHandler, Formatter
from logging.handlers import RotatingFileHandler
from sys import stdout, stderr

def my_logger(name, logfile=False, level='INFO', stream=True, rotate=False, std="stdout"):
    logger = getLogger(name)
    logger.handlers.clear()

    formatter = Formatter(
        "%(asctime)s %(levelname)s-%(module)s-%(funcName)s-%(lineno)d %(message)s"
    )

    ## stream
    if stream:
        if std == 'stdout':
            streamHandler = StreamHandler(stream=stdout)
        else:
            streamHandler = StreamHandler(stream=stderr)
        streamHandler.setFormatter(formatter)
        streamHandler.setLevel(level)
        logger.addHandler(streamHandler)

    if logfile:
        if rotate:
            fileHandler = RotatingFileHandler(logfile,  encoding='utf-8', maxBytes=10000, backupCount=5)
        else:
            fileHandler = FileHandler(logfile, encoding='utf-8', mode='a')
        fileHandler.setFormatter(formatter)
        fileHandler.setLevel(level)
        logger.addHandler(fileHandler)

    logger.setLevel('DEBUG')

    return logger
