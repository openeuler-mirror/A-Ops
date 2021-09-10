#!/bin/bash
ARCH=$(uname -m)
PROGRAM=$0
PRJ_DIR=$(dirname $(readlink -f "$0"))

TOOLS_DIR=${PRJ_DIR}/tools
SRC_DIR=${PRJ_DIR}/src
VMLINUX_DIR=${SRC_DIR}/include
LINUX_VER=$(uname -r)

function gen_vmlinux_header_file()
{
    cd ${TOOLS_DIR}
    if [ ! -f "bpftool" ];then
        ln -s bpftool_${ARCH} bpftool
    fi
    ./gen_vmlinux_h.sh
}

function add_bpftool() {
    cd ${TOOLS_DIR}
    if [ ! -f "bpftool" ];then
        ln -s bpftool_${ARCH} bpftool
    fi
}

function checkout_libbpf()
{
    cd ${PRJ_DIR}
    if [ ! -d "libbpf" ];then
	git clone https://github.com/libbpf/libbpf.git
        cd libbpf
        git checkout v0.3
    fi
}

function prepare_dep()
{
    yum install -y elfutils-devel
    if [ $? -ne 0 ];then
        echo "Error: elfutils-devel install failed"
        return 1
    fi

    yum install -y clang
    if [ $? -ne 0 ];then
        echo "Error: clang install failed"
        return 1
    fi
    V=`clang --version | grep version | awk -F ' ' '{print $3}' | awk -F . '{print $1}'`
    if [ "$V" -lt 10 ];then
        echo "Error: clange version need >= 10.x.x"
	return 1
    fi

    yum install -y llvm
    if [ $? -ne 0 ];then
        echo "Error: llvm install failed"
        return 1
    fi
    return 0
}

function compile_probe()
{
    VMLINUX_VER=${LINUX_VER%.*}
    MATCH_VMLINUX=linux_${VMLINUX_VER}.h

    cd ${VMLINUX_DIR}
    if [ -f ${MATCH_VMLINUX} ];then
        rm -f vmlinux.h
        ln -s ${MATCH_VMLINUX} vmlinux.h
        echo "debug: match vmlinux :" ${MATCH_VMLINUX}
    else
        echo "there no match vmlinux :" ${MATCH_VMLINUX}
    fi

    cd ${SRC_DIR}
    echo "=======Begin to compile ebpf-based probes======:" ${EBPF_PROBES}
    make
}

function compile_clean()
{
    cd ${SRC_DIR}
    make clean
}

if [ -z "$1"  -o  "$1" == "-h"  -o  "$1" == "--help" ];
then
    echo build.sh -h/--help : Show this message.
    echo build.sh    --check: Check the environment including arch/os/kernel/packages.
    echo build.sh -g/--gen  : Generate the linux header file.
    echo build.sh -c/--clean: Clean the built binary.
    echo build.sh -b/--build: Build all the probes.
    exit
fi

if [ "$1" == "--check" ];
then
    checkout_libbpf
    prepare_dep
    exit
fi

add_bpftool

if [ "$1" == "-g"  -o  "$1" == "--gen" ];
then
    gen_vmlinux_header_file
    exit
fi

if [ "$1" == "-b"  -o  "$1" == "--build" ];
then
    compile_probe
    exit
fi

if [ "$1" == "-c"  -o  "$1" == "--clean" ];
then
    compile_clean
    exit
fi
