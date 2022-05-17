ROOT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

Q = @

CLANG ?= clang
LLVM_STRIP ?= llvm-strip
BPFTOOL ?= $(ROOT_DIR)/../../tools/bpftool
LIBBPF_DIR = $(ROOT_DIR)/../.output
GOPHER_COMMON_DIR = $(ROOT_DIR)/../../../../../common
KERNEL_DIR = /lib/modules/$(shell uname -r)/build
UTIL_DIR ?= $(ROOT_DIR)../lib
UTIL_SRC ?= $(wildcard $(UTIL_DIR)/*.c)
UTIL_SRC += $(wildcard $(GOPHER_COMMON_DIR)/*.c)
INSTALL_DIR=/usr/bin/extends/ebpf.probe

ARCH = $(shell uname -m)
ifeq ($(ARCH), x86_64)
	ARCH = x86
else ifeq ($(ARCH), aarch64)
	ARCH = arm64
endif

KER_VER = $(shell uname -r | awk -F'-' '{print $$1}')
KER_VER_MAJOR = $(shell echo $(KER_VER) | awk -F'.' '{print $$1}')
KER_VER_MINOR = $(shell echo $(KER_VER) | awk -F'.' '{print $$2}')
KER_VER_PATCH = $(shell echo $(KER_VER) | awk -F'.' '{print $$3}')

KERNEL_DEVEL_VER = $(shell rpm -qi kernel-devel | grep -w Version | awk -F ': ' '{print $$2}')
KERNEL_DEVEL_REL = $(shell rpm -qi kernel-devel | grep -w Release | awk -F ': ' '{print $$2}')
KERNEL_DEVEL_DIR = /lib/modules/$(KERNEL_DEVEL_VER)-$(KERNEL_DEVEL_REL).$(shell uname -m)/build/include/generated
KERNEL_DEVEL_EXIST = $(shell if [ -d $(KERNEL_DEVEL_DIR) ]; then echo "kernel devel exist"; else echo "noexist"; fi)
ifeq ("$(KERNEL_DEVEL_EXIST)", "noexist")
    $(error, "error: can't find kernel devel rpm, pls check it.")
endif

EXTRA_CFLAGS ?= -g -O2 -Wall
EXTRA_CDEFINE ?= -D__TARGET_ARCH_$(ARCH)
CFLAGS := $(EXTRA_CFLAGS) $(EXTRA_CDEFINE)
CFLAGS += -DKER_VER_MAJOR=$(KER_VER_MAJOR) -DKER_VER_MINOR=$(KER_VER_MINOR) -DKER_VER_PATCH=$(KER_VER_PATCH)

BASE_INC := -I/usr/include \
            -I$(ROOT_DIR)../include \
            -I$(GOPHER_COMMON_DIR) \
            -I$(KERNEL_DEVEL_DIR) \
             -I$(LIBBPF_DIR)
