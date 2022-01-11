/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
 */
#ifndef __EBPF_UTIL_H__
#define __EBPF_UTIL_H__

#include <bpf/libbpf.h>
/* if eBPF probe need to be integrated by gala-gopher, should redefinition the macro */

#define BPF_UTIL_DESC(desc) 1

#define TM_STR_LEN 48
#ifndef AF_INET
#define AF_INET 2
#endif
#ifndef AF_INET6
#define AF_INET6 10
#endif

#define NIP6(addr)                                                                                  \
    ntohs((addr)[0]), ntohs(addr[1]), ntohs(addr[2]), ntohs(addr[3]), ntohs(addr[4]), ntohs(addr[5]), \
        (ntohs((addr)[6]) >> 8), (ntohs(addr[6]) & 0xff), (ntohs(addr[7]) >> 8), (ntohs(addr[7]) & 0xff)
#define NIP6_FMT "%04x:%04x:%04x:%04x:%04x:%04x:%u.%u.%u.%u"


/* get uprobe func offset */
int get_func_offset(char *proc_name, char *func_name, char *bin_file_path);

char *get_cur_time();

void ip_str(unsigned int family, unsigned char *ip, unsigned char *ip_str, unsigned int ip_str_size);

#endif
