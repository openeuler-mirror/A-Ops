include mk/var.mk

APPS = $(filter ./%/, $(dir $(shell find . -name Makefile)))

.PHONY: all clean install
all:  bpf apps
bpf: $(LIBBPF_OBJ)
# Build libbpf
$(LIBBPF_OBJ): $(wildcard $(LIBBPF_SRC)/*.[ch] $(LIBBPF_SRC)/Makefile)
	$(Q)$(MAKE) -C $(LIBBPF_SRC) BUILD_STATIC_ONLY=1                      \
                    OBJDIR=$(dir $@)/libbpf DESTDIR=$(dir $@)                 \
                    INCLUDEDIR= LIBDIR= UAPIDIR=                              \
                    install
apps:
	$(foreach app, $(APPS), make -s -C $(app);)

clean:
	rm -rf $(LIBBPF_DIR)
	$(foreach app, $(APPS), make -s clean -C $(app);)

install:
	$(foreach app, $(APPS), make -s install -C $(app);)
