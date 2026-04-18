import logging.config

from server.src.app.logging.logger_config import LOGGING_CONFIG

def setup_logging():
    logging.config.dictConfig(LOGGING_CONFIG)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)