ROOT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

Q = @

CLANG ?= clang
LLVM_STRIP ?= llvm-strip
BPFTOOL ?= $(ROOT_DIR)/../../tools/bpftool
LIBBPF_DIR = $(ROOT_DIR)/../.output

UTIL_DIR ?= $(ROOT_DIR)../lib
UTIL_SRC ?= $(wildcard $(UTIL_DIR)/*.c)
INSTALL_DIR=/usr/bin/extends/ebpf.probe

ARCH = $(shell uname -m)
ifeq ($(ARCH), x86_64)
	ARCH = x86
else ifeq ($(ARCH), aarch64)
	ARCH = arm64
endif

EXTRA_CFLAGS ?= -g -O2 -Wall
EXTRA_CDEFINE ?= -D__TARGET_ARCH_$(ARCH)
CFLAGS := $(EXTRA_CFLAGS) $(EXTRA_CDEFINE)

BASE_INC := -I/usr/include \
            -I$(ROOT_DIR)../include \
	    -I$(LIBBPF_DIR)
