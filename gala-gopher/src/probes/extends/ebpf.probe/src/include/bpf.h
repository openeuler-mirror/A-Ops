/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
 */
#ifndef __GOPHER_BPF_H__
#define __GOPHER_BPF_H__

#define __PROBE_MATCH_MAP_PIN_PATH "/sys/fs/bpf/probe/match_map"
struct __probe_key {
    unsigned int smp_id;
    unsigned int pid;
    long bp;
};

#define __PROBE_PARAM1 0
#define __PROBE_PARAM2 1
#define __PROBE_PARAM3 2
#define __PROBE_PARAM4 3
#define __PROBE_PARAM5 4
#define __PROBE_PARAM6 5
#define __PROBE_PARAM_MAX 6
struct __probe_val {
    long params[__PROBE_PARAM_MAX];
};

struct probe_val {
    struct __probe_val val;
};


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
            ({                                         \
                typeof(P) val;                         \
                bpf_probe_read(&val, sizeof(val), &P); \
                val;                                   \
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

#define __PROBE_MATCH_MAP_MAX_ENTRIES 1000
struct bpf_map_def SEC("maps") __probe_match_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct __probe_key),
    .value_size = sizeof(struct __probe_val),
    .max_entries = __PROBE_MATCH_MAP_MAX_ENTRIES,
};


static __always_inline void __get_probe_key(struct __probe_key *key, const long bp) {
    key->smp_id = bpf_get_smp_processor_id();
    key->pid = bpf_get_current_pid_tgid() >> 32;
    key->bp = bp;
}

static __always_inline void __get_probe_val(struct __probe_val *val,
                                                    const long p1,
                                                    const long p2,
                                                    const long p3,
                                                    const long p4,
                                                    const long p5,
                                                    const long p6) {
    val->params[__PROBE_PARAM1] = p1;
    val->params[__PROBE_PARAM2] = p2;
    val->params[__PROBE_PARAM3] = p3;
    val->params[__PROBE_PARAM4] = p4;
    val->params[__PROBE_PARAM5] = p5;
    val->params[__PROBE_PARAM6] = p6;
}

static __always_inline int __do_push_match_map(const struct __probe_key *key,
                                    const struct __probe_val* val) {
    return bpf_map_update_elem(&__probe_match_map, key, val, BPF_ANY);
}

#define KPROBE_RET(func, type) \
    bpf_section("kprobe/" #func) \
    void __kprobe_bpf_##func(struct type *ctx) { \
        int ret; \
        struct __probe_key __key = {0}; \
        struct __probe_val __val = {0}; \
        __get_probe_key(&__key, (const long)PT_REGS_FP(ctx)); \
        __get_probe_val(&__val, (const long)PT_REGS_PARM1(ctx), \
                               (const long)PT_REGS_PARM2(ctx), \
                               (const long)PT_REGS_PARM3(ctx), \
                               (const long)PT_REGS_PARM4(ctx), \
                               (const long)PT_REGS_PARM5(ctx), \
                               (const long)PT_REGS_PARM6(ctx)); \
        ret = __do_push_match_map(&__key, &__val); \
        if (ret < 0) { \
            bpf_printk("---KPROBE_RET[" #func "] push failed.\n"); \
        } \
    } \
    \
    bpf_section("kretprobe/" #func) \
    void __kprobe_ret_bpf_##func(struct type *ctx)

int __do_pop_match_map_entry(const struct __probe_key *key,
                                    struct __probe_val* val)
{
    struct __probe_val* tmp;
    tmp = bpf_map_lookup_elem(&__probe_match_map, (const void *)key);
    if (tmp == 0) {
        return -1;
    }
    val->params[__PROBE_PARAM1] = tmp->params[__PROBE_PARAM1];
    val->params[__PROBE_PARAM2] = tmp->params[__PROBE_PARAM2];
    val->params[__PROBE_PARAM3] = tmp->params[__PROBE_PARAM3];
    val->params[__PROBE_PARAM4] = tmp->params[__PROBE_PARAM4];
    val->params[__PROBE_PARAM5] = tmp->params[__PROBE_PARAM5];
    val->params[__PROBE_PARAM6] = tmp->params[__PROBE_PARAM6];
    return bpf_map_delete_elem(&__probe_match_map, (const void *)key);
}

#define PROBE_GET_PARMS(func, ctx, probe_val) \
    do { \
        int ret; \
        struct __probe_key __key = {0}; \
        struct __probe_val __val = {0}; \
        __get_probe_key(&__key, (const long)PT_REGS_FP(ctx)); \
        ret = __do_pop_match_map_entry((const struct __probe_key *)&__key, \
                                        &__val); \
        if (ret < 0) { \
            bpf_printk("---PROBE_GET_PARMS[" #func "] pop failed.\n"); \
        } else { \
        __builtin_memcpy(&probe_val.val, &__val, sizeof(struct __probe_val)); \
        } \
        \
    } while (0)

#define PROBE_PARM1(probe_val) (probe_val).val.params[__PROBE_PARAM1]
#define PROBE_PARM2(probe_val) (probe_val).val.params[__PROBE_PARAM2]
#define PROBE_PARM3(probe_val) (probe_val).val.params[__PROBE_PARAM3]
#define PROBE_PARM4(probe_val) (probe_val).val.params[__PROBE_PARAM4]
#define PROBE_PARM5(probe_val) (probe_val).val.params[__PROBE_PARAM5]
#define PROBE_PARM6(probe_val) (probe_val).val.params[__PROBE_PARAM6]

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

#define _(P)                                        \
    ({                                              \
        typeof(P) val;                              \
        bpf_probe_read_user(&val, sizeof(val), &P); \
        val;                                        \
    })

#define bpf_section(NAME) __attribute__((section(NAME), used))

#define UPROBE(func, type) \
    bpf_section("uprobe/" #func) \
    void ubpf_##func(struct type *ctx)

#define URETPROBE(func, type) \
    bpf_section("uretprobe/" #func) \
    void ubpf_ret_##func(struct type *ctx)


#define __PROBE_MATCH_MAP_MAX_ENTRIES 1000
struct bpf_map_def SEC("maps") __probe_match_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct __probe_key),
    .value_size = sizeof(struct __probe_val),
    .max_entries = __PROBE_MATCH_MAP_MAX_ENTRIES,
};


static __always_inline void __get_probe_key(struct __probe_key *key, const long bp) {
    key->smp_id = bpf_get_smp_processor_id();
    key->pid = bpf_get_current_pid_tgid() >> 32;
    key->bp = bp;
}

static __always_inline void __get_probe_val(struct __probe_val *val,
                                                    const long p1,
                                                    const long p2,
                                                    const long p3,
                                                    const long p4,
                                                    const long p5) {
    val->params[__PROBE_PARAM1] = p1;
    val->params[__PROBE_PARAM2] = p2;
    val->params[__PROBE_PARAM3] = p3;
    val->params[__PROBE_PARAM4] = p4;
    val->params[__PROBE_PARAM5] = p5;
}

static __always_inline int __do_push_match_map(const struct __probe_key *key,
                                    const struct __probe_val* val) {
    return bpf_map_update_elem(&__probe_match_map, key, val, BPF_ANY);
}

#define UPROBE_RET(func, type) \
    bpf_section("uprobe/" #func) \
    void __uprobe_bpf_##func(struct type *ctx) { \
        int ret; \
        struct __probe_key __key = {0}; \
        struct __probe_val __val = {0}; \
        __get_probe_key(&__key, (const long)PT_REGS_FP(ctx)); \
        __get_probe_val(&__val, (const long)PT_REGS_PARM1(ctx), \
                               (const long)PT_REGS_PARM2(ctx), \
                               (const long)PT_REGS_PARM3(ctx), \
                               (const long)PT_REGS_PARM4(ctx), \
                               (const long)PT_REGS_PARM5(ctx)); \
        ret = __do_push_match_map(&__key, &__val); \
        if (ret < 0) { \
            bpf_printk("---UPROBE_RET[" #func "] push failed.\n"); \
        } \
    } \
    \
    bpf_section("uretprobe/" #func) \
    void __uprobe_ret_bpf_##func(struct type *ctx)

int __do_pop_match_map_entry(const struct __probe_key *key,
                                    struct __probe_val* val)
{
    struct __probe_val* tmp;
    tmp = bpf_map_lookup_elem(&__probe_match_map, (const void *)key);
    if (tmp == 0) {
        return -1;
    }
    val->params[__PROBE_PARAM1] = tmp->params[__PROBE_PARAM1];
    val->params[__PROBE_PARAM2] = tmp->params[__PROBE_PARAM2];
    val->params[__PROBE_PARAM3] = tmp->params[__PROBE_PARAM3];
    val->params[__PROBE_PARAM4] = tmp->params[__PROBE_PARAM4];
    val->params[__PROBE_PARAM5] = tmp->params[__PROBE_PARAM5];
    return bpf_map_delete_elem(&__probe_match_map, (const void *)key);
}

#define PROBE_GET_PARMS(func, ctx, probe_val) \
    do { \
        int ret; \
        struct __probe_key __key = {0}; \
        struct __probe_val __val = {0}; \
        __get_probe_key(&__key, (const long)PT_REGS_FP(ctx)); \
        ret = __do_pop_match_map_entry((const struct __probe_key *)&__key, \
                                        &__val); \
        if (ret < 0) { \
            bpf_printk("---PROBE_GET_PARMS[" #func "] pop failed.\n"); \
        } else { \
        __builtin_memcpy(&probe_val.val, &__val, sizeof(struct __probe_val)); \
        } \
        \
    } while (0)

#define PROBE_PARM1(probe_val) (probe_val).val.params[__PROBE_PARAM1]
#define PROBE_PARM2(probe_val) (probe_val).val.params[__PROBE_PARAM2]
#define PROBE_PARM3(probe_val) (probe_val).val.params[__PROBE_PARAM3]
#define PROBE_PARM4(probe_val) (probe_val).val.params[__PROBE_PARAM4]
#define PROBE_PARM5(probe_val) (probe_val).val.params[__PROBE_PARAM5]

#endif

#if !defined( BPF_PROG_KERN ) && !defined( BPF_PROG_USER )

#include <bpf/libbpf.h>
#include <sys/resource.h>
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
        .rlim_cur   = EBPF_RLIM_INFINITY,
        .rlim_max   = EBPF_RLIM_INFINITY,
    };

    if (setrlimit(RLIMIT_MEMLOCK, &rlim_new)) {
        fprintf(stderr, "Failed to increase RLIMIT_MEMLOCK limit!\n");
        return 0;
    }
    return 1;
}

#define GET_MAP_OBJ(map_name) (skel->maps.map_name)
#define GET_MAP_FD(map_name) bpf_map__fd(skel->maps.map_name)
#define GET_PROG_FD(prog_name) bpf_program__fd(skel->progs.prog_name)

#define __PROBE_MATCH_MAP_PIN(ret) \
    do { \
        int __fd; \
        struct bpf_map *__map; \
        \
        __map = GET_MAP_OBJ(__probe_match_map); \
        __fd = bpf_obj_get(__PROBE_MATCH_MAP_PIN_PATH); \
        if (__fd > 0) { \
            ret = bpf_map__reuse_fd(__map, __fd); \
            break; \
        } \
        (ret) = bpf_map__pin(__map, __PROBE_MATCH_MAP_PIN_PATH); \
    } while (0)

#if UNIT_TESTING
#define LOAD(probe_name) \
    struct probe_name##_bpf *skel;                 \
    struct bpf_link *link[PATH_NUM];    \
    int current = 0;    \
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
            skel = NULL; \
            goto err; \
        } \
        __PROBE_MATCH_MAP_PIN(err); \
        if (err < 0) { \
            goto err; \
        } \
    } while (0)
#else
#define LOAD(probe_name) \
    struct probe_name##_bpf *skel;                 \
    struct bpf_link *link[PATH_NUM];    \
    int current = 0;    \
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
            skel = NULL; \
            goto err; \
        } \
        __PROBE_MATCH_MAP_PIN(err); \
        if (err < 0) { \
            goto err; \
        } \
    } while (0)
#endif


#define UNLOAD(probe_name) \
    do { \
	    int err; \
        if (skel != NULL) { \
            probe_name##_bpf__destroy(skel); \
        } \
        for (int i = 0; i < current; i++) { \
            err = bpf_link__destroy(link[i]); \
            if (err < 0) { \
                fprintf(stderr, "Failed to detach uprobe: %d\n", err); \
                break; \
            } \
        } \
    } while (0)


#define PATH_NUM   20
#define ELF_REAL_PATH(proc_name, elf_abs_path, container_id, elf_path, path_num) \
    do { \
        path_num = get_exec_file_path( #proc_name, elf_abs_path, #container_id, elf_path, PATH_NUM); \
        if ((path_num) <= 0) { \
            fprintf(stderr, "Failed to get proc(" #proc_name ") abs_path.\n"); \
            (void)free_exec_path_buf(elf_path, path_num); \
            break; \
        } \
    } while (0)

#define UBPF_ATTACH(probe_name, elf_path, func_name, error) \
    do { \
        int err; \
        long symbol_offset; \
        err = resolve_symbol_infos(elf_path, #func_name, NULL, &symbol_offset); \
        if (err < 0) { \
            fprintf(stderr, "Failed to get func(" #func_name ") in(%s) offset.\n", elf_path); \
            error = 0; \
            break; \
        } \
        \
        /* Attach tracepoint handler */ \
        link[current] = bpf_program__attach_uprobe( \
            skel->progs.ubpf_##probe_name, false /* not uretprobe */, -1, elf_path, symbol_offset); \
        err = libbpf_get_error(link[current]); \
        if (err) { \
            fprintf(stderr, "Failed to attach uprobe: %d\n", err); \
            error = 0; \
            break; \
        } \
        fprintf(stdout, "Success to attach uprobe to elf: %s\n", elf_path); \
        current += 1; \
        error = 1; \
    } while (0)

#define UBPF_RET_ATTACH(probe_name, elf_path, func_name, error) \
    do { \
        int err; \
        long symbol_offset; \
        err = resolve_symbol_infos(elf_path, #func_name, NULL, &symbol_offset); \
        if (err < 0) { \
            fprintf(stderr, "Failed to get func(" #func_name ") in(%s) offset.\n", elf_path); \
            error = 0; \
            break; \
        } \
        \
        /* Attach tracepoint handler */ \
        link[current] = bpf_program__attach_uprobe( \
            skel->progs.ubpf_ret_##probe_name, true /* uretprobe */, -1, elf_path, symbol_offset); \
        err = libbpf_get_error(link[current]); \
        if (err) { \
            fprintf(stderr, "Failed to attach uprobe: %d\n", err); \
            error = 0; \
            break; \
        } \
        fprintf(stdout, "Success to attach uretprobe to elf: %s\n", elf_path); \
        current += 1; \
        error = 1; \
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
