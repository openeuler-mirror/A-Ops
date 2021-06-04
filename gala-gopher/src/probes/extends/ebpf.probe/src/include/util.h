#ifndef __EBPF_UTIL_H__
#define __EBPF_UTIL_H__

/* if eBPF probe need to be integrated by gala-gopher, should redefinition the macro*/
#define UNIT_TESTING 1

#if UNIT_TESTING
#define EBPF_RLIM_INFINITY  RLIM_INFINITY
#else
#define EBPF_RLIM_INFINITY  100*1024*1024 // 100M
#endif

#define BPF_UTIL_DESC(desc) 1

#define TM_STR_LEN 48
#define AF_INET 2
#define AF_INET6 10

#define NIP6(addr)                                                                                  \
    ntohs(addr[0]), ntohs(addr[1]), ntohs(addr[2]), ntohs(addr[3]), ntohs(addr[4]), ntohs(addr[5]), \
        (ntohs(addr[6]) >> 8), (ntohs(addr[6]) & 0xff), (ntohs(addr[7]) >> 8), (ntohs(addr[7]) & 0xff)
#define NIP6_FMT "%04x:%04x:%04x:%04x:%04x:%04x:%u.%u.%u.%u"

typedef void (*arg_opt_proc_func)(char opt, char *arg, int idx);
int args_parse(int argc, char **argv, char *opt_str, arg_opt_proc_func opt_proc);

/* get uprobe func offset */
int get_func_offset(char *proc_name, char *binary_file_path, char *func_name);

char *get_cur_time();

void ip_str(unsigned int family, unsigned char *ip, unsigned char *ip_str, unsigned int ip_str_size);
int set_memlock_rlimit(void);
#endif