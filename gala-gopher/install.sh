#!/bin/bash

PROGRAM=$0
PROJECT_FOLDER=$(dirname $(readlink -f "$0"))

GOPHER_BIN_FILE=${PROJECT_FOLDER}/gala-gopher
GOPHER_BIN_TARGET_DIR=/usr/bin
GOPHER_CONF_FILE=${PROJECT_FOLDER}/config/gala-gopher.conf
GOPHER_CONF_TARGET_DIR=/opt/gala-gopher

cd ${PROJECT_FOLDER}

if [ ! -f ${GOPHER_BIN_FILE} ]; then
    echo "${GOPHER_BIN_FILE} not exist. please check if build success."
    exit 1
fi

if [ ! -f ${GOPHER_CONF_FILE} ]; then
    echo "${GOPHER_CONF_FILE} not exist. please check ./config dir."
    exit 1
fi

if [ ! -d ${GOPHER_CONF_TARGET_DIR} ]; then
    mkdir ${GOPHER_CONF_TARGET_DIR}
fi

cp -f ${GOPHER_BIN_FILE} ${GOPHER_BIN_TARGET_DIR}
cp -f ${GOPHER_CONF_FILE} ${GOPHER_CONF_TARGET_DIR}

echo "install ${GOPHER_BIN_FILE} success."
echo "install ${GOPHER_CONF_FILE} success."
