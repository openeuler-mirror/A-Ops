#ifndef __GOPHER_BPF_H__
#define __GOPHER_BPF_H__


#ifdef BPF_PROG_KERN

#include "vmlinux.h"
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#define bpf_section(NAME) __attribute__((section(NAME), used))

#define KPROBE(func, type) \
    bpf_section("kprobe/" #func) \
    void bpf_##func(struct type *ctx)

#define KRETPROBE(func, type) \
    bpf_section("kretprobe/" #func) \
    void bpf_ret_##func(struct type *ctx)

#define KRAWTRACE(func, type) \
    bpf_section("raw_tracepoint/" #func) \
    void bpf_raw_trace_##func(struct type *ctx)

#define _(P)                                   \
			({										   \
				typeof(P) val;						   \
				bpf_probe_read(&val, sizeof(val), &P); \
				val;								   \
			})

#if defined(__TARGET_ARCH_x86)
#define PT_REGS_PARM6(x) ((x)->r9)
#elif defined(__TARGET_ARCH_arm64)
#define PT_REGS_ARM64 const volatile struct user_pt_regs
#define PT_REGS_PARM6(x) (((PT_REGS_ARM64 *)(x))->regs[5])
#endif

static __always_inline struct sock *sock_get_by_fd(int fd, struct task_struct *task)
{
    struct files_struct *files = _(task->files);
    struct fdtable *fdt = _(files->fdt);
    struct file **ff = _(fdt->fd);
    struct file *f;
	unsigned int max_fds = _(fdt->max_fds);

	if (fd >= max_fds) {
		return 0;
	}
	
    bpf_probe_read_kernel(&f, sizeof(struct file *), (struct file *)(ff + fd));
    if (!f) {
        return 0;
    }

    struct inode *fi = _(f->f_inode);
    unsigned short imode = _(fi->i_mode);
    if (((imode & 00170000) != 00140000)) {
        return 0;
    }

    struct socket *sock = _(f->private_data);
    struct sock *sk = _(sock->sk);
    return sk;
}

#endif

#ifdef BPF_PROG_USER
#include <linux/bpf.h>
#include <linux/ptrace.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>


#if defined(__TARGET_ARCH_x86)
#define PT_REGS_PARM6(x) ((x)->r9)
#elif defined(__TARGET_ARCH_arm64)
#define PT_REGS_ARM64 const volatile struct user_pt_regs
#define PT_REGS_PARM6(x) (((PT_REGS_ARM64 *)(x))->regs[5])
#endif

#define _(P)                                   		\
    ({                                         		\
        typeof(P) val;                         		\
        bpf_probe_read_user(&val, sizeof(val), &P); \
        val;                                   		\
    })

#define bpf_section(NAME) __attribute__((section(NAME), used))

#define UPROBE(func, type) \
    bpf_section("uprobe/" #func) \
    void ubpf_##func(struct type *ctx)

#define URETPROBE(func, type) \
    bpf_section("uretprobe/" #func) \
    void ubpf_ret_##func(struct type *ctx)

#endif

#if !defined( BPF_PROG_KERN ) && !defined( BPF_PROG_USER ) 
#include <bpf/libbpf.h>
#include "util.h"

static __always_inline int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args)
{
	return vfprintf(stderr, format, args);
}

#define UNIT_TESTING 1

#if UNIT_TESTING
#define EBPF_RLIM_INFINITY  RLIM_INFINITY
#else
#define EBPF_RLIM_INFINITY  100*1024*1024 // 100M
#endif

static __always_inline int set_memlock_rlimit(void)
{
	struct rlimit rlim_new = {
		.rlim_cur	= EBPF_RLIM_INFINITY,
		.rlim_max	= EBPF_RLIM_INFINITY,
	};

	if (setrlimit(RLIMIT_MEMLOCK, &rlim_new)) {
		fprintf(stderr, "Failed to increase RLIMIT_MEMLOCK limit!\n");
		return 0;
	}
	return 1;
}


#if UNIT_TESTING
#define LOAD(probe_name) \
    struct probe_name##_bpf *skel;                 \
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
        skel = probe_name##_bpf__open_and_load(); \
        if (!skel) { \
            fprintf(stderr, "Failed to open BPF skeleton\n"); \
            goto err; \
        } \
        /* Attach tracepoint handler */ \
        err = probe_name##_bpf__attach(skel); \
        if (err) { \
            fprintf(stderr, "Failed to attach BPF skeleton\n"); \
            probe_name##_bpf__destroy(skel); \
            skel = NULL;\
            goto err; \
        }\
    } while (0)
#else
#define LOAD(probe_name) \
    struct probe_name##_bpf *skel;                 \
    do { \
        int err; \
        /* Set up libbpf errors and debug info callback */ \
        libbpf_set_print(libbpf_print_fn); \
        \
        /* Open load and verify BPF application */ \
        skel = probe_name##_bpf__open_and_load(); \
        if (!skel) { \
            fprintf(stderr, "Failed to open BPF skeleton\n"); \
            goto err; \
        } \
        /* Attach tracepoint handler */ \
        err = probe_name##_bpf__attach(skel); \
        if (err) { \
            fprintf(stderr, "Failed to attach BPF skeleton\n"); \
            probe_name##_bpf__destroy(skel); \
            skel = NULL;\
            goto err; \
        }\
    } while (0)
#endif


#define UNLOAD(probe_name) \
    if (skel != NULL) {\
        probe_name##_bpf__destroy(skel);\
    }\


#define GET_MAP_FD(map_name) bpf_map__fd(skel->maps.map_name)
#define GET_PROG_FD(prog_name) bpf_program__fd(skel->progs.prog_name)


#define __BIN_FILE_PATH_LEN 256
#define UBPF_ATTACH(probe_name,proc_name,func_name) \
	do { \
	    int err; \
	    long offset; \
	    char bin_file_path[__BIN_FILE_PATH_LEN] = {0}; \
		\
	    offset = get_func_offset( #proc_name, #func_name, bin_file_path); \
	    if (offset <= 0) { \
	        printf("Failed to get func(" #func_name ") offset.\n"); \
	        goto err;\
	    } \
        \
	    /* Attach tracepoint handler */ \
	    skel->links.ubpf_##func_name = bpf_program__attach_uprobe( \
	        skel->progs.ubpf_##func_name, false /* not uretprobe */, -1, bin_file_path, offset); \
	    err = libbpf_get_error(skel->links.ubpf_##func_name); \
	    if (err) { \
	        fprintf(stderr, "Failed to attach uprobe: %d\n", err); \
	        goto err;\
	    } \
    } while (0)

#define UBPF_RET_ATTACH(probe_name,proc_name,func_name) \
	do { \
	    int err; \
	    long offset; \
	    char bin_file_path[__BIN_FILE_PATH_LEN] = {0}; \
		\
	    offset = get_func_offset( #proc_name, #func_name, bin_file_path); \
	    if (offset <= 0) { \
	        printf("Failed to get func(" #func_name ") offset.\n"); \
	        goto err;\
	    } \
        \
	    /* Attach tracepoint handler */ \
		skel->links.ubpf_ret_##func_name = bpf_program__attach_uprobe( \
			skel->progs.ubpf_ret_##func_name, true /* uretprobe */, -1, bin_file_path, offset); \
		err = libbpf_get_error(skel->links.ubpf_ret_##func_name); \
		if (err) { \
			fprintf(stderr, "Failed to attach uprobe: %d\n", err); \
			goto err; \
		} \
    } while (0)

static __always_inline struct perf_buffer* create_pref_buffer(int map_fd, perf_buffer_sample_fn cb)
{
	struct perf_buffer_opts pb_opts = {};
	struct perf_buffer *pb;
    int ret;
    
	pb_opts.sample_cb = cb;
	pb = perf_buffer__new(map_fd, 8, &pb_opts);
    if (pb == NULL){
		fprintf(stderr, "ERROR: perf buffer new failed\n");
		return NULL;
    }
	ret = libbpf_get_error(pb);
	if (ret) {
		fprintf(stderr, "ERROR: failed to setup perf_buffer: %d\n", ret);
		perf_buffer__free(pb);
        return NULL;
	}
    return pb;
}

static __always_inline void poll_pb(struct perf_buffer *pb, int timeout_ms)
{
    int ret;
    
	while ((ret = perf_buffer__poll(pb, timeout_ms)) >= 0) {
        ;
	}
    return;
}

#endif

#endif
