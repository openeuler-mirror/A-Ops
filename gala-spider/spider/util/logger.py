import os
import logging
from logging import Logger
from logging.handlers import RotatingFileHandler

LOG_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
formatter = logging.Formatter(LOG_FMT)

console_hdl = logging.StreamHandler()
console_hdl.setFormatter(formatter)

logger: Logger = logging.getLogger()
logger.addHandler(console_hdl)
logger.setLevel(logging.INFO)


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

    file_hdl = RotatingFileHandler(filename=log_path, maxBytes=max_bytes, backupCount=backup_count)
    file_hdl.setFormatter(formatter)

    logger.addHandler(file_hdl)
    logger.setLevel(log_level)
