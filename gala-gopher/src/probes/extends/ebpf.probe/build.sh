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
    ./gen_vmlinux_h.sh
}

function compile_probe()
{
    cd ${SRC_DIR}
    make clean
    make
}

function checkout_libbpf()
{
    if [ ! -f "libbpf" ];then
	git clone https://github.com/libbpf/libbpf.git
        cd libbpf
        git checkout v0.3
    fi
}

# checkout libbpf code
#git submodule update --init --recursive
checkout_libbpf
gen_vmlinux_header_file
compile_probe
