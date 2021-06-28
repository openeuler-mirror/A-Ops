#!/bin/bash

PROGRAM=$0
PROJECT_FOLDER=$(dirname $(readlink -f "$0"))
EXT_PROBE_FOLDER=${PROJECT_FOLDER}/src/probes/extends
EXT_PROBE_INSTALL_LIST=`find ${EXT_PROBE_FOLDER} -maxdepth 2 | grep "\<install.sh\>"`

function install_daemon_bin()
{
    GOPHER_BIN_FILE=${PROJECT_FOLDER}/gala-gopher
    GOPHER_BIN_TARGET_DIR=/usr/bin

    cd ${PROJECT_FOLDER}
    if [ ! -f ${GOPHER_BIN_FILE} ]; then
        echo "${GOPHER_BIN_FILE} not exist. please check if build success."
        exit 1
    fi

    # install gala-gopher bin
    cp -f ${GOPHER_BIN_FILE} ${GOPHER_BIN_TARGET_DIR}
    echo "install ${GOPHER_BIN_FILE} success."

}

function install_conf()
{
    GOPHER_CONF_FILE=${PROJECT_FOLDER}/config/gala-gopher.conf
    GOPHER_CONF_TARGET_DIR=/opt/gala-gopher

    cd ${PROJECT_FOLDER}
    if [ ! -f ${GOPHER_CONF_FILE} ]; then
        echo "${GOPHER_CONF_FILE} not exist. please check ./config dir."
        exit 1
    fi

    # install gala-gopher.conf
    if [ ! -d ${GOPHER_CONF_TARGET_DIR} ]; then
        mkdir ${GOPHER_CONF_TARGET_DIR}
    fi
    cp -f ${GOPHER_CONF_FILE} ${GOPHER_CONF_TARGET_DIR}
    echo "install ${GOPHER_CONF_FILE} success."

}

function install_meta()
{
    GOPHER_META_DIR=/opt/gala-gopher/meta

    cd ${PROJECT_FOLDER}

    # install meta files
    if [ ! -d ${GOPHER_META_DIR} ]; then
        mkdir -p ${GOPHER_META_DIR}
    fi
    META_FILES=`find ${PROJECT_FOLDER}/src -name "*.meta"`
    for file in ${META_FILES}
    do
        cp ${file} ${GOPHER_META_DIR}
    done
    echo "install meta file success."

}

function install_extend_probes()
{
    GOPHER_EXTEND_PROBE_DIR=/opt/gala-gopher/extend_probes
    if [ ! -d ${GOPHER_EXTEND_PROBE_DIR} ]; then
        mkdir -p ${GOPHER_EXTEND_PROBE_DIR}
    fi

    cd ${PROJECT_FOLDER}

    # Search for install.sh in extend probe directory
    cd ${EXT_PROBE_FOLDER}
    for INSTALL_PATH in ${EXT_PROBE_INSTALL_LIST}
    do
        echo "install path:" ${INSTALL_PATH}
        ${INSTALL_PATH} ${GOPHER_EXTEND_PROBE_DIR}
    done
}

# main process
install_daemon_bin
install_conf
install_meta
#install_extend_probes


