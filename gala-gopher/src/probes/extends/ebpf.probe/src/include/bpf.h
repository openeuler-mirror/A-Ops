#ifndef __GOPHER_BPF_H__
#define __GOPHER_BPF_H__


#define bpf_section(NAME) __attribute__((section(NAME), used))

#define KPROBE(func, type) \
    bpf_section("kprobe/" #func) \
    void bpf_##func(struct type *ctx)

#define KRETPROBE(func, type) \
    bpf_section("kretprobe/" #func) \
    void bpf_##func(struct type *ctx)

#define KRAWTRACE(func, type) \
    bpf_section("raw_tracepoint/" #func) \
    void bpf_##func(struct type *ctx)


#if UNIT_TESTING
#define LOAD(probe_name) \
    struct probe_name##probe_bpf *skel;                 \
    do { \
        int err; \
        /* Set up libbpf errors and debug info callback */ \
        libbpf_set_print(libbpf_print_fn); \
        \
        /* Bump RLIMIT_MEMLOCK  allow BPF sub-system to do anything */ \
        if (set_memlock_rlimit() == 0) { \
            return NULL; \
        } \
        /* Open load and verify BPF application */ \
        skel = probe_name##probe_bpf__open_and_load(); \
        if (!skel) { \
            fprintf(stderr, "Failed to open BPF skeleton\n"); \
            break; \
        } \
        /* Attach tracepoint handler */ \
        err = probe_name##probe_bpf__attach(skel); \
        if (err) { \
            fprintf(stderr, "Failed to attach BPF skeleton\n"); \
            probe_name##probe_bpf__destroy(skel); \
            skel = NULL;\
            break; \
        }\
    } while (0)
#else
#define LOAD(probe_name) \
    struct probe_name##probe_bpf *skel;                 \
    do { \
        int err; \
        /* Set up libbpf errors and debug info callback */ \
        libbpf_set_print(libbpf_print_fn); \
        \
        /* Open load and verify BPF application */ \
        skel = probe_name##probe_bpf__open_and_load(); \
        if (!skel) { \
            fprintf(stderr, "Failed to open BPF skeleton\n"); \
            break; \
        } \
        /* Attach tracepoint handler */ \
        err = probe_name##probe_bpf__attach(skel); \
        if (err) { \
            fprintf(stderr, "Failed to attach BPF skeleton\n"); \
            probe_name##probe_bpf__destroy(skel); \
            skel = NULL;\
            break; \
        }\
    } while (0)
#endif


#define UNLOAD(probe_name) \
    if (skel != NULL) {\
        probe_name##probe_bpf__destroy(skel);\
    }\


#define _(P)                                   \
        ({                                         \
            typeof(P) val;                         \
            bpf_probe_read(&val, sizeof(val), &P); \
            val;                                   \
        })


#endif
