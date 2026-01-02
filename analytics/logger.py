import logging
import sys
from logging.handlers import NTEventLogHandler
from logging.handlers import SysLogHandler

LOGGER_NAME = "PulseConnector"


def setup_logger():
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    if sys.platform.startswith("win"):
        _setup_windows_logger(logger)
    else:
        _setup_linux_logger(logger)

    return logger


def _setup_linux_logger(logger):
    try:
        handler = SysLogHandler(address="/dev/log")
    except Exception:
        # fallback (algunos sistemas)
        handler = SysLogHandler(address=("localhost", 514))

    formatter = logging.Formatter(
        "%(name)s[%(process)d]: %(levelname)s %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)


def _setup_windows_logger(logger):
    handler = NTEventLogHandler(
        appname="PulseConnector",
        logtype="Application"
    )

    formatter = logging.Formatter(
        "%(levelname)s %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    '''
    IMPLEMENT:
    
        from logger import setup_logger
        
        log = setup_logger()
        
        log.info("PulseConnector started")
        log.warning("Slow query detected")
        log.error("Database connection failed")
    '''