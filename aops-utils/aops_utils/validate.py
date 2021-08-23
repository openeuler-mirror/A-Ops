#!/usr/bin/python3
"""
Description: validate funtion.
"""
import os
from datetime import datetime

from .log.log import LOGGER


def validate_path(path, file=True):
    """
    judge whether the path is valid.

    Args:
        path (str): path need to be checked.

    Returns:
        bool
    """
    if not os.path.exists(path):
        LOGGER.error("%s does not exist.", path)
        return False

    if not os.access(path, os.R_OK):
        LOGGER.error('Cannot access %s', path)
        return False

    if file and os.path.isdir(path):
        LOGGER.error("Couldn't parse directory %s ", path)
        return False

    return True


def validate_time(time, time_format):
    """
    judge whether the time is matched to format.

    Args:
        time (str): time need to be checked.
        time_format (str): time format.

    Returns:
        bool
    """
    try:
        datetime.strptime(time, time_format)
        return True
    except ValueError as error:
        LOGGER.error(error)
        return False
