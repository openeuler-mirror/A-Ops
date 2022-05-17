#!/bin/bash

PROGRAM=$0
PROJECT_FOLDER=$(dirname $(readlink -f "$0"))

PROBES_FOLDER=${PROJECT_FOLDER}/src/probes
PROBES_PATH_LIST=`find ${PROJECT_FOLDER}/src/probes -maxdepth 1 | grep ".probe\>"`
EXT_PROBE_FOLDER=${PROJECT_FOLDER}/src/probes/extends
EXT_PROBE_BUILD_LIST=`find ${EXT_PROBE_FOLDER} -maxdepth 2 | grep "\<build.sh\>"`
PROBES_LIST=""
PROBES_C_LIST=""
PROBES_META_LIST=""
KERNEL_DEV=""

DAEMON_FOLDER=${PROJECT_FOLDER}/src/daemon

TAILOR_PATH=${PROJECT_FOLDER}/tailor.conf
TAILOR_PATH_TMP=${TAILOR_PATH}.tmp

function get_kernel_devel_dir()
{
    ver=`rpm -qi kernel-devel | grep -w Version | awk -F ': ' '{print $2}'`
    rel=`rpm -qi kernel-devel | grep -w Release | awk -F ': ' '{print $2}'`
    dir=/lib/modules/${ver}-${rel}.$(uname -m)/build/include/generated
    if [ -d $dir ]; then
        KERNEL_DEV=$dir
    else
        echo "error: can't find kernel devel rpm, pls check it."
        return 1
    fi
}

function load_tailor()
{
    if [ -f ${TAILOR_PATH} ]; then
        cp ${TAILOR_PATH} ${TAILOR_PATH_TMP}

        sed -i '/^$/d' ${TAILOR_PATH_TMP}
        sed -i 's/ //g' ${TAILOR_PATH_TMP}
        sed -i 's/^/export /' ${TAILOR_PATH_TMP}
        eval `cat ${TAILOR_PATH_TMP}`

        rm -rf ${TAILOR_PATH_TMP}
    fi
}

function __get_probes_source_files()
{
    one_probe_src_list=`find $1 -name "*.c"`
    for one_file in ${one_probe_src_list}
    do
        file_name=${one_file#*$1/}
        file_name=${file_name%.*}

        if [[ ! $file_name = $2 && ! $file_name = $2_daemon ]]; then
            PROBES_C_LIST=${PROBES_C_LIST}\;${1}/${file_name}.c
        fi
    done
}

function prepare_probes()
{
    if [ ${PROBES} ]; then
        # check tailor env
        PROBES_PATH_LIST=$(echo "$PROBES_PATH_LIST" | grep -Ev "$PROBES")
        echo "prepare probes after tailor: " ${PROBES_PATH_LIST}
    fi

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

        __get_probes_source_files $PROBE_PATH $PROBE_NAME

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

function compile_daemon_release()
{
    cd ${DAEMON_FOLDER}
    rm -rf build
    mkdir build
    cd build

    cmake -DGOPHER_DEBUG="0" -DKERNEL_DEV="${KERNEL_DEV}" -DPROBES_C_LIST="${PROBES_C_LIST}" -DPROBES_LIST="${PROBES_LIST}" -DPROBES_META_LIST="${PROBES_META_LIST}" ..
    make
}

function compile_daemon_debug()
{
    cd ${DAEMON_FOLDER}
    rm -rf build
    mkdir build
    cd build

    cmake -DGOPHER_DEBUG="1" -DKERNEL_DEV="${KERNEL_DEV}" -DPROBES_C_LIST="${PROBES_C_LIST}" -DPROBES_LIST="${PROBES_LIST}" -DPROBES_META_LIST="${PROBES_META_LIST}" ..
    make
}


function compile_daemon_clean()
{
    rm -rf ${PROJECT_FOLDER}/gala-gopher
    rm -rf ${PROJECT_FOLDER}/gopher-ctl
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

function compile_extend_probes_clean()
{
    # Search for build.sh in probe directory
    echo "==== Begin to clean extend probes ===="
    cd ${EXT_PROBE_FOLDER}
    for BUILD_PATH in ${EXT_PROBE_BUILD_LIST}
    do
        echo "==== BUILD_PATH: " ${BUILD_PATH}
        ${BUILD_PATH} --clean
    done
}

function compile_extend_probes_debug()
{
    # Search for build.sh in probe directory
    echo "==== Begin to compile debug extend probes ===="
    cd ${EXT_PROBE_FOLDER}
    for BUILD_PATH in ${EXT_PROBE_BUILD_LIST}
    do
        echo "==== BUILD_PATH: " ${BUILD_PATH}
        ${BUILD_PATH} --build --debug
    done
}

function compile_extend_probes_release()
{
    # Search for build.sh in probe directory
    echo "==== Begin to compile release extend probes ===="
    cd ${EXT_PROBE_FOLDER}
    for BUILD_PATH in ${EXT_PROBE_BUILD_LIST}
    do
        echo "==== BUILD_PATH: " ${BUILD_PATH}
        ${BUILD_PATH} --build
    done
}


# Check dependent packages and install automatically
function prepare_dependence()
{

    # for build framework
    yum install -y cmake
    if [ $? -ne 0 ];then
        echo "Error: Failed to install cmake."
        return 1
    fi

    # for gala-gopher framework sending message to kafka
    yum install -y librdkafka-devel
    if [ $? -ne 0 ];then
        echo "Error: Failed to install librdkafka-devel."
        return 1
    fi

    # for gala-gopher framework http server
    yum install -y libmicrohttpd-devel
    if [ $? -ne 0 ];then
        echo "Error: Failed to install libmicrohttpd-devel."
        return 1
    fi

    # for gala-gopher configrations
    yum install -y libconfig-devel
    if [ $? -ne 0 ];then
        echo "Error: Failed to install libconfig-devel."
        return 1
    fi

    yum install -y uthash-devel
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install uthash-devel."
        return 1
    fi

    return 0
}

function help()
{
    echo build.sh --help :Show this message.
    echo build.sh --check :Check the environment including arch/os/kernel/packages.
    echo build.sh --debug :Build gala-gopher debug version.
    echo build.sh --release :Build gala-gopher release version.
    echo build.sh --clean :Clean gala-gopher build objects.
}

if [ "$1" == "--help" ]; then
    help
    exit
fi

if [ "$1" == "--check" ]; then
    prepare_dependence
fi
if [ $? -ne 0 ];then
    echo "Error: prepare dependence softwares failed"
    exit
fi

if [ "$1" = "--release" ];then
    load_tailor
    get_kernel_devel_dir
    prepare_probes
    compile_daemon_release
    compile_extend_probes_release
    clean_env
    exit
fi

if [ "$1" = "--debug" ];then
    load_tailor
    get_kernel_devel_dir
    prepare_probes
    compile_daemon_debug
    compile_extend_probes_debug
    clean_env
    exit
fi

if [ "$1" = "--clean" ];then
    compile_daemon_clean
    compile_extend_probes_clean
    exit
fi
help

