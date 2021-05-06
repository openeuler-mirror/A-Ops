#!/bin/bash

PROGRAM=$0
PROJECT_FOLDER=$(dirname $(readlink -f "$0"))

PROBES_FOLDER=${PROJECT_FOLDER}/../src/probes
PROBES_PATH_LIST=`find ${PROJECT_FOLDER}/../src/probes -maxdepth 1 | grep ".probe\>"`
PROBES_LIST=""
PROBES_C_LIST=""
PROBES_META_LIST=""

TEST_FOLDER=${PROJECT_FOLDER}

echo "PROJECT_FOLDER:"
echo ${PROJECT_FOLDER}
echo "PROBES_PATH_LIST:"
echo ${PROBES_PATH_LIST}

function prepare_probes()
{
    cd ${PROBES_FOLDER}
    for PROBE_PATH in ${PROBES_PATH_LIST}
    do
        PROBE_NAME=${PROBE_PATH##*/}
        PROBE_NAME=${PROBE_NAME%.*}
        rm -f ${PROBE_PATH}/${PROBE_NAME}_daemon.c
        cp -f ${PROBE_PATH}/${PROBE_NAME}.c ${PROBE_PATH}/${PROBE_NAME}_daemon.c
        sed -i "s/int main(/int probe_main_${PROBE_NAME}(/g" ${PROBE_PATH}/${PROBE_NAME}_daemon.c

        if [ x"$PROBES_C_LIST" = x ];then
            PROBES_C_LIST=${PROBE_PATH}/${PROBE_NAME}_daemon.c
        else
            PROBES_C_LIST=${PROBES_C_LIST}\;${PROBE_PATH}/${PROBE_NAME}_daemon.c
        fi
        
        if [ x"$PROBES_LIST" = x ];then
            PROBES_LIST=${PROBE_NAME}
        else
            PROBES_LIST=${PROBES_LIST}" "${PROBE_NAME}
        fi

        if [ x"$PROBES_META_LIST" = x ];then
            PROBES_META_LIST=${PROBE_PATH}/${PROBE_NAME}.meta
        else
            PROBES_META_LIST=${PROBES_META_LIST}" "${PROBE_PATH}/${PROBE_NAME}.meta
        fi
    done

    echo "PROBES_C_LIST:"
    echo ${PROBES_C_LIST}
    echo "PROBES_META_LIST:"
    echo ${PROBES_META_LIST}
    cd -
}

function compile_test()
{
    cd ${TEST_FOLDER}
    cd test_probes
    rm -rf build
    mkdir build
    cd build

    cmake -DPROBES_C_LIST="${PROBES_C_LIST}" -DPROBES_LIST="${PROBES_LIST}" -DPROBES_META_LIST="${PROBES_META_LIST}" ..
    make
}

function clean_env()
{
    cd ${PROBES_FOLDER}
    for PROBE_PATH in ${PROBES_PATH_LIST}
    do
        PROBE_NAME=${PROBE_PATH##*/}
        PROBE_NAME=${PROBE_NAME%.*}

        rm -f ${PROBE_PATH}/${PROBE_NAME}_daemon.c
    done
}

function run_test()
{
    cd ${TEST_FOLDER}
    ./probes_test
}

prepare_probes
compile_test
clean_env
run_test

