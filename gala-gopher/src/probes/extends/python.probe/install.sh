#!/bin/sh
PROGRAM=$0
PRJ_DIR=$(dirname $(readlink -f "$0"))

INSTALL_FILES="redis.probe/redis_probe.py"

if [ $# -eq 1 ]; then
    # copy to specify dir
    cd ${PRJ_DIR}
    \cp ${INSTALL_FILES} $1
fi