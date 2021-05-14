#!/bin/sh
PROGRAM=$0
PRJ_DIR=$(dirname $(readlink -f "$0"))
MAKE_DIR=${PRJ_DIR}/src

cd ${MAKE_DIR}
make install
