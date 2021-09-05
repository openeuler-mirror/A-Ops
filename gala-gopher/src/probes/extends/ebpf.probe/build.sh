#!/bin/bash
ARCH=$(uname -m)
PROGRAM=$0
PRJ_DIR=$(dirname $(readlink -f "$0"))

TOOLS_DIR=${PRJ_DIR}/tools
SRC_DIR=${PRJ_DIR}/src
#echo ${PRJ_DIR}
#echo ${TOOLS_DIR}
#echo ${SRC_DIR}
function gen_vmlinux_header_file()
{
    cd ${TOOLS_DIR}
    if [ ! -f "bpftool" ];then
	ln -s bpftool_${ARCH} bpftool
    fi
}

function compile_probe()
{
    cd ${SRC_DIR}
    echo "=======compile_probe:" ${EBPF_PROBES}
    make
}

function checkout_libbpf()
{
    cd ${PRJ_DIR}
    if [ ! -f "libbpf" ];then
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

function compile_clean()
{
    cd ${SRC_DIR}
    make clean
}

if [ "$1" = "clean" ];then
    compile_clean
    exit
fi
if [ "$1" != "package" ]; then
    prepare_dep
fi
if [ $? -ne 0 ];then
    echo "Error: prepare dependence softwares failed"
    exit
fi
checkout_libbpf
gen_vmlinux_header_file
compile_probe
