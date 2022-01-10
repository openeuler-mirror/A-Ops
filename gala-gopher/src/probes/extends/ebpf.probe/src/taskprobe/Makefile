include ../mk/var.mk
INCLUDES = $(BASE_INC)

APP := taskprobe

DEPS := $(patsubst %.bpf.c, %.bpf.o, $(wildcard *.bpf.c))
DEPS += $(patsubst %.bpf.c, %.skel.h, $(wildcard *.bpf.c))

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

INCLUDES += -I$(LIBBPF_SRC)
app: $(APP)
%: %.c $(UTIL_SRC) $(LIBBPF_OBJ)
	$(CC) $(CFLAGS) $(INCLUDES) $^ -lelf -lz -o $@

clean:
	rm -rf $(DEPS)
	rm -rf $(APP)

install:
	mkdir -p $(INSTALL_DIR)
	cp $(APP) $(INSTALL_DIR)
