import os
import logging
from logging import Logger
from logging.handlers import RotatingFileHandler

logger: Logger = None


def init_logger(name, log_conf):
    global logger
    logger = logging.getLogger(name)

    log_path = log_conf.get('log_path')
    max_bytes = log_conf.get('max_size') * 1000 * 1000
    backup_count = log_conf.get('backup_count')
    log_level = log_conf.get('log_level', logging.INFO)

    log_path = os.path.realpath(log_path)
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - "
                                  "%(filename)s:%(lineno)d - %(message)s")
    handler = RotatingFileHandler(filename=log_path, maxBytes=max_bytes, backupCount=backup_count)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(log_level)
