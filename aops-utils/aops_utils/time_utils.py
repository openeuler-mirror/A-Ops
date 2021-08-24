import sys
import time
from datetime import datetime

from .log.log import LOGGER
from .validate import validate_time

TIME_FORMAT = '%Y%m%d-%H:%M:%S'


def time_transfer(start_time, end_time):
    """
    Transfer formated time to POSIX timestamp.

    Args:
        start_time (str): start time, set to 0 if None.
        end_time (str): end time, set to current time if None.

    Returns:
        tuple: e.g. (0, 1605077202)
    """
    # time_format = config.global_config.get_value('global', 'time_format')
    if start_time is None:
        start_time = 0
    else:
        if '-' not in start_time:
            start_time += '-0:0:0'
        if not validate_time(start_time, TIME_FORMAT):
            LOGGER.error(
                'The start time format is not correct, please refer to %s', TIME_FORMAT)
            sys.exit(0)
        else:
            start_time_struct = datetime.strptime(start_time, TIME_FORMAT)
            # Return integer POSIX timestamp.
            start_time = max(int(start_time_struct.timestamp()), 0)

    now = int(time.time())

    if end_time is None:
        # if end time is not specified, use the current time
        # end_time = int(time.time())
        end_time = now
    else:
        if '-' not in end_time:
            end_time += '-23:59:59'
        if not validate_time(end_time, TIME_FORMAT):
            LOGGER.error(
                'The end time format is not correct, please refer to %s', TIME_FORMAT)
            sys.exit(0)
        else:
            end_time_struct = datetime.strptime(end_time, TIME_FORMAT)
            end_time = min(int(end_time_struct.timestamp()), now)

    if start_time > end_time:
        LOGGER.error('The time range is not correct, please check again.')
        sys.exit(0)

    return start_time, end_time
