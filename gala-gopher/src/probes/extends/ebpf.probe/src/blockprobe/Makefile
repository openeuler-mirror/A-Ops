include ../mk/var.mk
INCLUDES = $(BASE_INC)

APP := blockprobe

BPF_C := $(wildcard *.bpf.c)
DEPS := $(patsubst %.bpf.c, %.bpf.o, $(BPF_C))
DEPS += $(patsubst %.bpf.c, %.skel.h, $(BPF_C))

SRC_C := $(filter-out $(BPF_C), $(wildcard *.c))
SRC_C += $(UTIL_SRC)

.PHONY: all clean install

all: pre deps app
pre: $(OUTPUT)
deps: $(DEPS)
# build bpf code
%.bpf.o: %.bpf.c
	$(CLANG) $(CFLAGS) -target bpf $(INCLUDES) -c $(filter %.c,$^) -o $@
	$(LLVM_STRIP) -g $@

# build skel.h
%.skel.h: %.bpf.o
	$(BPFTOOL) gen skeleton $< > $@

app: $(APP)
%: %.c $(SRC_C)
	$(CC) $(CFLAGS) $(INCLUDES) $^ $(LINK_TARGET) -o $@

clean:
	rm -rf $(DEPS)
	rm -rf $(APP)

install:
	mkdir -p $(INSTALL_DIR)
	cp $(APP) $(INSTALL_DIR)

