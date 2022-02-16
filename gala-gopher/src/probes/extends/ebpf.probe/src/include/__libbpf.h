/******************************************************************************
 * Copyright (c) Huawei Technologies Co., Ltd. 2021. All rights reserved.
 * gala-gopher licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Author: Mr.lu
 * Create: 2021-09-28
 * Description: bpf header
 ******************************************************************************/
#ifndef __GOPHER_LIB_BPF_H__
#define __GOPHER_LIB_BPF_H__


#if !defined( BPF_PROG_KERN ) && !defined( BPF_PROG_USER )

#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include <sys/resource.h>
#include "task.h"
#include "elf_reader.h"
#include "util.h"

#define EBPF_RLIM_INFINITY  100*1024*1024 // 100M

static __always_inline int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args)
{
    return vfprintf(stderr, format, args);
}

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

#define __PIN_SHARE_MAP(map_name, map_path) \
    do { \
        int __fd; \
        struct bpf_map *__map; \
        \
        __map = GET_MAP_OBJ(map_name); \
        (void)bpf_map__pin(__map, map_path); \
        __fd = bpf_obj_get(map_path); \
        (void)printf("======>SHARE map(" #map_name ") pin FD=%d.\n", __fd); \
    } while (0)

#define __PIN_SHARE_MAP_ALL \
        do { \
            __PIN_SHARE_MAP(__probe_match_map, __PROBE_MATCH_MAP_PIN_PATH); \
            __PIN_SHARE_MAP(__task_map, SHARE_MAP_TASK_PATH); \
        } while (0)

#define LOAD(probe_name) \
    struct probe_name##_bpf *skel;                 \
    struct bpf_link *link[PATH_NUM];    \
    int current = 0;    \
    do { \
        int err; \
        /* Set up libbpf errors and debug info callback */ \
        (void)libbpf_set_print(libbpf_print_fn); \
        \
        /* Bump RLIMIT_MEMLOCK  allow BPF sub-system to do anything */ \
        if (set_memlock_rlimit() == 0) { \
            return NULL; \
        } \
        /* Open load and verify BPF application */ \
        skel = probe_name##_bpf__open_and_load(); \
        if (!skel) { \
            (void)fprintf(stderr, "Failed to open BPF skeleton\n"); \
            goto err; \
        } \
        /* Attach tracepoint handler */ \
        err = probe_name##_bpf__attach(skel); \
        if (err) { \
            (void)fprintf(stderr, "Failed to attach BPF skeleton\n"); \
            probe_name##_bpf__destroy(skel); \
            skel = NULL; \
            goto err; \
        } \
        __PIN_SHARE_MAP_ALL; \
    } while (0)

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

#define LOAD_PROBE(probe_name, probe) \
    struct probe_name##_bpf *skel;                 \
    do { \
        int err; \
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
        __PIN_SHARE_MAP_ALL; \
        probe = skel; \
    } while (0)

#define UNLOAD_PROBE(probe_name, probe) \
    do { \
        int err; \
        if (probe != NULL) { \
            probe_name##_bpf__destroy(probe); \
        } \
    } while (0)


#define ELF_REAL_PATH(proc_name, elf_abs_path, container_id, elf_path, path_num) \
    do { \
        path_num = get_exec_file_path( #proc_name, (const char *)elf_abs_path, #container_id, elf_path, PATH_NUM); \
        if ((path_num) <= 0) { \
            (void)fprintf(stderr, "Failed to get proc(" #proc_name ") abs_path.\n"); \
            free_exec_path_buf(elf_path, path_num); \
            break; \
        } \
    } while (0)

#define UBPF_ATTACH(probe_name, elf_path, func_name, error) \
    do { \
        int err; \
        uint64_t symbol_offset; \
        err = resolve_symbol_infos((const char *)elf_path, #func_name, NULL, &symbol_offset); \
        if (err < 0) { \
            (void)fprintf(stderr, "Failed to get func(" #func_name ") in(%s) offset.\n", elf_path); \
            error = 0; \
            break; \
        } \
        \
        /* Attach tracepoint handler */ \
        link[current] = bpf_program__attach_uprobe( \
            skel->progs.ubpf_##probe_name, false /* not uretprobe */, -1, elf_path, (size_t)symbol_offset); \
        err = libbpf_get_error(link[current]); \
        if (err) { \
            (void)fprintf(stderr, "Failed to attach uprobe: %d\n", err); \
            error = 0; \
            break; \
        } \
        (void)fprintf(stdout, "Success to attach uprobe to elf: %s\n", elf_path); \
        current += 1; \
        error = 1; \
    } while (0)

#define UBPF_RET_ATTACH(probe_name, elf_path, func_name, error) \
    do { \
        int err; \
        uint64_t symbol_offset; \
        err = resolve_symbol_infos((const char *)elf_path, #func_name, NULL, &symbol_offset); \
        if (err < 0) { \
            (void)fprintf(stderr, "Failed to get func(" #func_name ") in(%s) offset.\n", elf_path); \
            error = 0; \
            break; \
        } \
        \
        /* Attach tracepoint handler */ \
        link[current] = bpf_program__attach_uprobe( \
            skel->progs.ubpf_ret_##probe_name, true /* uretprobe */, -1, elf_path, (size_t)symbol_offset); \
        err = libbpf_get_error(link[current]); \
        if (err) { \
            (void)fprintf(stderr, "Failed to attach uprobe: %d\n", err); \
            error = 0; \
            break; \
        } \
        (void)fprintf(stdout, "Success to attach uretprobe to elf: %s\n", elf_path); \
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
