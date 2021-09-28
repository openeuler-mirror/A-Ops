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
 * Author: algorithmofdish
 * Create: 2021-09-28
 * Description: provide gala-gopher epbf util functions
 ******************************************************************************/
#ifndef __EBPF_UTIL_H__
#define __EBPF_UTIL_H__

#include <bpf/libbpf.h>
/* if eBPF probe need to be integrated by gala-gopher, should redefinition the macro*/
#define UNIT_TESTING 1

#if UNIT_TESTING
#define EBPF_RLIM_INFINITY  RLIM_INFINITY
#else
#define EBPF_RLIM_INFINITY  100*1024*1024 // 100M
#endif

#define BPF_UTIL_DESC(desc) 1

#define TM_STR_LEN 48
#ifndef AF_INET
#define AF_INET 2
#endif
#ifndef AF_INET6
#define AF_INET6 10
#endif

#define NIP6(addr)                                                                                  \
    ntohs(addr[0]), ntohs(addr[1]), ntohs(addr[2]), ntohs(addr[3]), ntohs(addr[4]), ntohs(addr[5]), \
        (ntohs(addr[6]) >> 8), (ntohs(addr[6]) & 0xff), (ntohs(addr[7]) >> 8), (ntohs(addr[7]) & 0xff)
#define NIP6_FMT "%04x:%04x:%04x:%04x:%04x:%04x:%u.%u.%u.%u"

typedef void (*arg_opt_proc_func)(char opt, char *arg, int idx);
int args_parse(int argc, char **argv, char *opt_str, arg_opt_proc_func opt_proc);

/* get uprobe func offset */
int get_func_offset(char *proc_name, char *func_name, char *bin_file_path);

char *get_cur_time();

void ip_str(unsigned int family, unsigned char *ip, unsigned char *ip_str, unsigned int ip_str_size);
int set_memlock_rlimit(void);

struct perf_buffer* create_pref_buffer(int map_fd, perf_buffer_sample_fn cb);
void poll_pb(struct perf_buffer *pb, int timeout_ms);
#endif
