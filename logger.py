import logging
import os

def get_logger() -> logging.Logger:
    logging.basicConfig(filename = 'page_error.log', level = logging.WARNING)
    return logging.getLogger('page_error_logger')