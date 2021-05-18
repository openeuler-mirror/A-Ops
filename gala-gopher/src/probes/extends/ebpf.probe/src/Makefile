# SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause)
OUTPUT := .output
CLANG ?= clang
LLVM_STRIP ?= llvm-strip
BPFTOOL ?= $(abspath ../tools/bpftool)
LIBBPF_SRC := $(abspath ../libbpf/src)
LIBBPF_OBJ := $(abspath $(OUTPUT)/libbpf.a)
#INCLUDES := -I$(OUTPUT)
UTIL_DIR ?= $(abspath ./lib)
INCLUDES := -I$(OUTPUT) -I../libbpf/include/uapi \
	    -Iinclude

UTIL_SRC = $(wildcard $(UTIL_DIR)/*.c)
UTIL_OBJ=$(patsubst %.c,%.o,$(UTIL_SRC))
$(info $(UTIL_SRC))
CFLAGS := -g -Wall
INSTALL_DIR=/usr/bin/extends/ebpf.probe

ARCH = $(shell uname -m)
ifeq ($(ARCH), x86_64)
	ARCH = x86
else ifeq ($(ARCH), aarch64)
	ARCH = arm64
endif

# add probe
APPS := tcpprobe/tcpprobe 
APPS := killprobe/killprobe 

APPS_DIR = $(dir $(APPS))
OUTPUT_APPS_DIR = $(addprefix $(OUTPUT)/, $(APPS_DIR))
APPS_INC = $(addprefix -I./, $(OUTPUT_APPS_DIR))

INCLUDES += $(APPS_INC)

ifeq ($(V),1)
	Q =
	msg =
else
	Q = @
	msg = @printf '  %-8s %s%s\n'					\
		      "$(1)"						\
		      "$(patsubst $(abspath $(OUTPUT))/%,%,$(2))"	\
		      "$(if $(3), $(3))";
	MAKEFLAGS += --no-print-directory
endif

.PHONY: all
all: $(APPS)

.PHONY: clean
clean:
	$(call msg,CLEAN)
	$(Q)rm -rf $(OUTPUT) $(APPS) $(UTIL_OBJ)

OUT_DIR = $(OUTPUT) $(OUTPUT_APPS_DIR) $(OUTPUT)/libbpf
$(info $(OUT_DIR))
$(OUT_DIR):
	$(Q)mkdir -p $(OUT_DIR)

# Build final application
$(APPS): %: $(OUTPUT)/%.o $(LIBBPF_OBJ) $(UTIL_OBJ) | $(OUTPUT)
	$(call msg,BINARY,$@)
	$(Q)$(CC) $(CFLAGS) $(INCLUDES) $^ -lelf -lz -o $@

$(patsubst %,$(OUTPUT)/%.o,$(APPS)): %.o: %.skel.h

# Build user-space code
$(OUTPUT)/%.o: %.c $(wildcard %.h) | $(OUTPUT)
	$(call msg,CC,$@)
	$(Q)$(CC) $(CFLAGS) $(INCLUDES) -c $(filter %.c,$^) -o $@

# Generate BPF skeletons
$(OUTPUT)/%.skel.h: $(OUTPUT)/%.bpf.o | $(OUTPUT)
	$(call msg,GEN-SKEL,$@)
	$(Q)$(BPFTOOL) gen skeleton $< > $@

# Build BPF code
$(OUTPUT)/%.bpf.o: %.bpf.c $(LIBBPF_OBJ) | $(OUTPUT)
	$(call msg,BPF,$@)
	$(Q)$(CLANG) -g -O2 -target bpf -D__TARGET_ARCH_$(ARCH)		      \
		     $(INCLUDES) -c $(filter %.c,$^) -o $@
	$(Q)$(LLVM_STRIP) -g $@

# Build libbpf
$(LIBBPF_OBJ): $(wildcard $(LIBBPF_SRC)/*.[ch] $(LIBBPF_SRC)/Makefile) | $(OUTPUT)/libbpf
	$(call msg,LIB,$@)
	$(Q)$(MAKE) -C $(LIBBPF_SRC) BUILD_STATIC_ONLY=1		      \
		    OBJDIR=$(dir $@)/libbpf DESTDIR=$(dir $@)		      \
		    INCLUDEDIR= LIBDIR= UAPIDIR=			      \
		    install
$(UTIL_OBJ): $(UTIL_SRC)
	$(CC) $(CFLAGS) $(INCLUDES) -c $(filter %.c,$^) -o $@
# delete failed targets
.DELETE_ON_ERROR:

# keep intermediate (.skel.h, .bpf.o, etc) targets
.SECONDARY:

$(info $(APPS) $(INSTALL_DIR))
.PHONY: install
install:
	mkdir -p $(INSTALL_DIR)
	cp $(APPS) $(INSTALL_DIR)
