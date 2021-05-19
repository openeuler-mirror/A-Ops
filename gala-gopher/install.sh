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

# install gala-gopher bin
cp -f ${GOPHER_BIN_FILE} ${GOPHER_BIN_TARGET_DIR}
echo "install ${GOPHER_BIN_FILE} success."

# install gala-gopher.conf
cp -f ${GOPHER_CONF_FILE} ${GOPHER_CONF_TARGET_DIR}
echo "install ${GOPHER_CONF_FILE} success."

# install meta files
if [ ! -d ${GOPHER_CONF_TARGET_DIR}/meta ]; then
    mkdir ${GOPHER_CONF_TARGET_DIR}/meta
fi

META_FILES=`find ${PROJECT_FOLDER}/src -name "*.meta"`
for file in ${META_FILES}
do
    cp ${file} ${GOPHER_CONF_TARGET_DIR}/meta
done
echo "install meta file success."

