#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <time.h>
#include <errno.h>
#include <signal.h>
#include <unistd.h>
#include <sys/resource.h>
#include "util.h"

#define BUF_TMP_LEN 256
#if BPF_UTIL_DESC("args parse")
int args_parse(int argc, char **argv, char *opt_str, arg_opt_proc_func opt_proc)
{
    int ch;
    if (!opt_str || !opt_proc) {
        return -1;
    }
    while ((ch = getopt(argc, argv, opt_str)) != -1) {
        if (!optarg) {
            return -1;
        }
        opt_proc(ch, optarg, optind);
    }
    return 0;
}
#endif
#if BPF_UTIL_DESC("get user space proc func offset")
/*
 * 1. 使用 ps -e | grep /usr/sbin/nginx | awk '{print $1}'获得nginx进程ID
 * 2. 使用cat /proc/<进程ID>/maps | grep r-xp 获得进程开始地址start和映射在文件中的偏移量
 * 3. start - offset获得进程基地址
 * 4. 使用 objdump -t /usr/sbin/nginx | grep <func_name> | awk \'{print $1}\'获得函数偏移地址
 */
static int get_bin_process_id(char *bin_name)
{
    FILE *fp = NULL;
    char buffer[BUF_TMP_LEN] = {0};
    char cmd[BUF_TMP_LEN] = {0};

    if (bin_name == NULL) {
        return -1;
    }
    snprintf(cmd, BUF_TMP_LEN, "ps -e | grep %s | awk \'{print $1}\'", bin_name);
    fp = popen(cmd, "r");
    while (NULL != fgets(buffer, 10, fp)) {
        break;
    }
    pclose(fp);
    return (int)atoi(buffer);
}
static long get_bin_base_addr(char *bin_name, int *pid)
{
    int bin_pid;
    size_t start, offset;
    char buf[BUF_TMP_LEN];
    char cmd_buf[BUF_TMP_LEN] = {0};
    FILE *f;

    if (bin_name == NULL || !pid) {
        fprintf(stderr, "get_bin_base_addr input bin_name NULL\n");
        return -1;
    }

    bin_pid = get_bin_process_id(bin_name);
    if (bin_pid < 0) {
        fprintf(stderr, "get_bin_process_id return error\n");
        return -1;
    }

    *pid = bin_pid;
    snprintf(cmd_buf, BUF_TMP_LEN, "/proc/%d/maps", bin_pid);
    f = fopen(cmd_buf, "r");
    if (!f) {
        return -errno;
    }

    while (fscanf(f, "%zx-%*x %s %zx %*[^\n]\n", &start, buf, &offset) == 3) {
        if (strcmp(buf, "r-xp") == 0) {
            fclose(f);
            return start - offset;
        }
    }

    fclose(f);
    return -1;
}

static long get_bin_file_path(char *bin_name, char *buf)
{
    int bin_pid;
    char cmd_buf[BUF_TMP_LEN] = {0};
    int res;

    if (bin_name == NULL) {
        fprintf(stderr, "get_bin_file_path input bin_name NULL\n");
        return -1;
    }

    bin_pid = get_bin_process_id(bin_name);
    if (bin_pid < 0) {
        fprintf(stderr, "get_bin_process_id return error\n");
        return -1;
    }

    snprintf(cmd_buf, BUF_TMP_LEN, "/proc/%d/exe", bin_pid);
    res = readlink(cmd_buf, buf, BUF_TMP_LEN - 1);
    if (res < 0 || res >= (BUF_TMP_LEN - 1)) {
        fprintf(stderr, "get_bin_file_path readlink fail.\n");
        return -1;
    }
    buf[res] = '\0';
    return 0;
}

static long get_bin_func_offset(char *bin_file_path, char *func_name)
{
    FILE *fp = NULL;
    char cmd[BUF_TMP_LEN] = {0};
    char buf[BUF_TMP_LEN] = {0};

    snprintf(cmd, BUF_TMP_LEN, "objdump -t %s | grep -w %s | awk \'{print $1}\'", bin_file_path, func_name);
    fp = popen(cmd, "r");
    while (NULL != fgets(buf, 32, fp)) {
        break;
    }
    pclose(fp);
    return strtol(buf, NULL, 16);
}

/* get uprobe func offset */
int get_func_offset(char *proc_name, char *func_name, char *bin_file_path)
{
    int pid;
    int err;
    long base_addr, func_offset;

    if (!proc_name || !func_name || !bin_file_path) {
        return -1;
    }

    base_addr = get_bin_base_addr(proc_name, &pid);
    if (base_addr < 0) {
        fprintf(stderr, "Failed to determine process's load address\n");
        return -1;
    }

    err = get_bin_file_path(proc_name, bin_file_path);
    if (err < 0) {
        fprintf(stderr, "Failed to get bin file real path.\n");
        return -1;
    }

    func_offset = get_bin_func_offset(bin_file_path, func_name);
    if (func_offset <= base_addr) {
        return -1;
    }
    return (long)(func_offset - base_addr);
}
#endif

#if BPF_UTIL_DESC("util funcs")
char *get_cur_time()
{
    /* return time str, ex: 2021/5/17 19:56:03 */
    static char tm[TM_STR_LEN] = {0};
    struct tm *tmp_ptr;
    time_t t;

    time(&t);

    tmp_ptr = localtime(&t);
    snprintf(tm,
        TM_STR_LEN,
        "%d/%d/%d %02d:%02d:%02d",
        (1900 + tmp_ptr->tm_year),
        (1 + tmp_ptr->tm_mon),
        tmp_ptr->tm_mday,
        tmp_ptr->tm_hour,
        tmp_ptr->tm_min,
        tmp_ptr->tm_sec);
    return tm;
}

void ip6_str(unsigned char *ip6, unsigned char *ip_str, unsigned int ip_str_size)
{
    unsigned short *addr = (unsigned short *)ip6;
    int i, j;
    char str[48];
    /* 1. format ipv6 address */
    snprintf((char *)str, ip_str_size, NIP6_FMT, NIP6(addr));
    /* 2. compress */
    for (i = 0, j = 0; str[j] != '\0'; i++, j++) {
        if (str[j] == '0' && (j == 0 || ip_str[i - 1] == ':')) {  //the first 0
            if (str[j + 1] != '0') {        // 0XXX
                j = j + 1;
            } else if (str[j + 2]!='0') {   // 00XX
                j = j + 2;
            } else {                        // 000X 0000
                j = j + 3;
            }
        }
        ip_str[i] = str[j];
    }
    ip_str[i] = '\0';
    return;
}

void ip_str(unsigned int family, unsigned char *ip, unsigned char *ip_str, unsigned int ip_str_size)
{
    if (family == AF_INET6) {
        (void)ip6_str(ip, ip_str, ip_str_size);
        return;
    }

    snprintf((char *)ip_str, ip_str_size, "%u.%u.%u.%u", ip[0], ip[1], ip[2], ip[3]);
    return;
}
#endif

int set_memlock_rlimit(void)
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
