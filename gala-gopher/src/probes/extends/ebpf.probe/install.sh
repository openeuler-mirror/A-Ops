#!/bin/sh
PROGRAM=$0
PRJ_DIR=$(dirname $(readlink -f "$0"))
MAKE_DIR=${PRJ_DIR}/src

EXT_PATH=/usr/bin/extends
INSTALL_PATH=${EXT_PATH}/ebpf.probe

cd ${MAKE_DIR}
make install

if [ $# -eq 1 ]; then
    # copy to specify dir
    \cp ${INSTALL_PATH}/* $1
    rm -rf ${EXT_PATH}
fi