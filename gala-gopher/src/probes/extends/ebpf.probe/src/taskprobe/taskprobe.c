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
 * Author: sinever
 * Create: 2021-10-25
 * Description: task_probe user prog
 ******************************************************************************/
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/resource.h>

#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif

#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif

#include "bpf.h"
#include "args.h"
#include "taskprobe.skel.h"
#include "thread_io.skel.h"
#include "process_io.skel.h"
#include "taskprobe_net.skel.h"
#include "taskprobe.h"
#include "task.h"

#define TASK_COMM "/proc/%d/comm"
#define TASK_CWD_FILE "/proc/%d/cwd"
#define TASK_EXE_FILE "/proc/%d/exe"

#define OO_NAME_TASK "task"
#define OO_THREAD_NAME  "thread"
#define OO_PROCESS_NAME "process"

#define OUTPUT_PATH "/sys/fs/bpf/probe/__taskprobe_output"
#define PERIOD_PATH "/sys/fs/bpf/probe/__taskprobe_period"

static int g_task_bin_map_fd;
static volatile sig_atomic_t stop = 0;
static struct probe_params tp_params = {.period = DEFAULT_PERIOD,
                                        .task_whitelist = {0}};

static struct task_name_t task_range[] = {
    {"go",              TASK_TYPE_APP},
    {"java",            TASK_TYPE_APP},
    {"python",          TASK_TYPE_APP},
    {"python3",         TASK_TYPE_APP},
    {"nginx",           TASK_TYPE_APP},
    {"redis",           TASK_TYPE_APP},
    {"redis-server",    TASK_TYPE_APP},
    {"redis-client",    TASK_TYPE_APP},
    {"redis-cli",       TASK_TYPE_APP},
    {"dhclient",        TASK_TYPE_OS},
    {"NetworkManager",  TASK_TYPE_OS},
    {"dbus",            TASK_TYPE_OS},
    {"rpcbind",         TASK_TYPE_OS},
    {"systemd",         TASK_TYPE_OS},
    {"scsi",            TASK_TYPE_KERN},
    {"softirq",         TASK_TYPE_KERN},
    {"kworker",         TASK_TYPE_KERN}
};

static void sig_int(int signal)
{
    stop = 1;
}

static int do_read_link(const char* fname, char *buf, unsigned int buf_len)
{
    int len;
    len = readlink(fname, buf, buf_len);
    if (len < 0) {
        return -1;
    }

    if (len < buf_len)
        buf[len] = '\0';
    return 0;
}

static int do_read_file(const char* fname, char *buf, unsigned int buf_len)
{
    char cmd[COMMAND_LEN];
    char line[LINE_BUF_LEN];
    FILE *f = NULL;

    if (access(fname, 0) != 0) {
        return -1;
    }

    cmd[0] = 0;
    line[0] = 0;
    (void)snprintf(cmd, COMMAND_LEN, "/usr/bin/cat %s", fname);
    f = popen(cmd, "r");
    if (f == NULL) {
        return -1;
    }
    if (fgets(line, LINE_BUF_LEN, f) == NULL) {
        (void)pclose(f);
        return -1;
    }
    
    SPLIT_NEWLINE_SYMBOL(line);
    (void)strncpy(buf, line, buf_len);
    (void)pclose(f);
    return 0;
}
                                    
static int get_task_exe(int pid, char *buf, unsigned int buf_len)
{
    char fname[COMMAND_LEN];

    fname[0] = 0;
    (void)snprintf(fname, COMMAND_LEN, TASK_EXE_FILE, pid);
    return do_read_link(fname, buf, buf_len);
}

static int get_task_cwd(int pid, char *buf, unsigned int buf_len)
{
    char fname[COMMAND_LEN];

    fname[0] = 0;
    (void)snprintf(fname, COMMAND_LEN, TASK_CWD_FILE, pid);
    return do_read_link(fname, buf, buf_len);
}

static int get_task_comm(int pid, char *buf, unsigned int buf_len)
{
    char fname[COMMAND_LEN];

    fname[0] = 0;
    (void)snprintf(fname, COMMAND_LEN, TASK_COMM, pid);
    return do_read_file(fname, buf, buf_len);
}

static void load_daemon_task(int app_fd, int task_map_fd)
{
    struct probe_process ckey = {0};
    struct probe_process nkey = {0};
    int flag;
    int ret = -1;

    while (bpf_map_get_next_key(app_fd, &ckey, &nkey) != -1) {
        ret = bpf_map_lookup_elem(app_fd, &nkey, &flag);
        if (ret == 0) {
            load_daemon_task_by_name(task_map_fd, (const char *)nkey.name);
            DEBUG("[TASKPROBE]: load daemon process '%s'.\n", nkey.name);
        }
        ckey = nkey;
    }

    uint32_t index, size = sizeof(task_range) / sizeof(task_range[0]);
    for (index = 0; index < size; index++) {
        if (task_range[index].type != TASK_TYPE_APP) {

            load_daemon_task_by_name(task_map_fd, (const char *)task_range[index].name);
            DEBUG("[TASKPROBE]: load daemon process '%s'.\n", task_range[index].name);
        }
    }
    return;
}

static void load_task_range(int fd)
{
    int flag = 1;
    struct probe_process pname;
    uint32_t index, size = sizeof(task_range) / sizeof(task_range[0]);
    for (index = 0; index < size; index++) {
        if (task_range[index].type == TASK_TYPE_APP) {
            (void)memset(pname.name, 0, MAX_PROCESS_NAME_LEN);
            (void)strcpy(pname.name, task_range[index].name);

            /* update probe_proc_map */
            (void)bpf_map_update_elem(fd, &pname, &flag, BPF_ANY);

            DEBUG("[TASKPROBE]: load probe process name '%s'.\n", pname.name);
        }
    }
}

static void load_task_wl(int fd)
{
    FILE *f = NULL;
    char line[MAX_PROCESS_NAME_LEN];
    struct probe_process pname;
    int flag = 1;

    f = fopen(tp_params.task_whitelist, "r");
    if (f == NULL) {
        return;
    }
    while (!feof(f)) {
        (void)memset(line, 0, MAX_PROCESS_NAME_LEN);
        if (fgets(line, MAX_PROCESS_NAME_LEN, f) == NULL) {
            goto out;
        }
        SPLIT_NEWLINE_SYMBOL(line);
        if (strlen(line) == 0) {
            continue;
        }
        (void)memset(pname.name, 0, MAX_PROCESS_NAME_LEN);
        (void)strncpy(pname.name, line, MAX_PROCESS_NAME_LEN);

        /* update probe_proc_map */
        (void)bpf_map_update_elem(fd, &pname, &flag, BPF_ANY);

        DEBUG("[TASKPROBE]: load probe process name '%s'.\n", pname.name);
    }
out:
    fclose(f);
    return;
}

static int jinfo_get_label_info(int pid, char *label, char *buf, int buf_len)
{
    FILE *f = NULL;
    char command[COMMAND_LEN];
    char line[LINE_BUF_LEN];
    int len = (buf_len <= LINE_BUF_LEN) ? buf_len : LINE_BUF_LEN;

    command[0] = 0;
    line[0] = 0;
    (void)snprintf(command, COMMAND_LEN, "jinfo %d | grep %s | awk '{print $3}'", pid, label);
    f = popen(command, "r");
    if (f == NULL)
        return -1;
    if (fgets(line, len, f) == NULL) {
        (void)pclose(f);
        return -1;
    }
    SPLIT_NEWLINE_SYMBOL(line);
    (void)strncpy(buf, line, len - 1);

    (void)pclose(f);
    return 0;
}

static int update_java_process_info(int pid, char *java_command, char *java_classpath)
{
    java_command[0] = 0;
    java_classpath[0] = 0;
    if (jinfo_get_label_info(pid, TASK_PROBE_JAVA_COMMAND, java_command, JAVA_COMMAND_LEN) < 0) {
        printf("java process get command fail.\n");
        return -1;
    }
    if (jinfo_get_label_info(pid, TASK_PROBE_JAVA_CLASSPATH, java_classpath, JAVA_CLASSPATH_LEN) < 0) {
        printf("java process get command fail.\n");
        return -1;
    }
    return 0;
}

static void get_task_bin_data(int bin_fd, struct task_bin* bin, struct task_key* key)   // process
{
    char java_command[JAVA_COMMAND_LEN];
    char java_classpath[JAVA_CLASSPATH_LEN];

    if (bin->comm[0] == 0) {
        (void)get_task_comm(key->tgid, bin->comm, MAX_PROCESS_NAME_LEN);
    }

    /* exe file name */ 
    if (bin->exe_file[0] == 0) {
        (void)get_task_exe(key->tgid, bin->exe_file, TASK_EXE_FILE_LEN);
    }

    /* exec file name */
    if (strstr(bin->comm, "java") != NULL && bin->exec_file[0] == 0) {
        /* java */
        (void)update_java_process_info(key->tgid, (char *)java_command, (char *)java_classpath);
        (void)strncpy(bin->exec_file, java_command, TASK_EXE_FILE_LEN);
    } else if (strstr(bin->comm, "python") != NULL || strstr(bin->comm, "go") != NULL) {
        /* python/go run */
        (void)get_task_cwd(key->tgid, bin->exec_file, TASK_EXE_FILE_LEN);
    } else if (bin->exec_file[0] == 0) {
        /* c/c++/go */
        (void)strncpy(bin->exec_file, bin->exe_file, TASK_EXE_FILE_LEN);
    } else {
        ; // nothing to do.
    }

    /* update task bin */
    (void)bpf_map_update_elem(bin_fd, key, bin, BPF_ANY);

    return;
}

static void update_task_bin_map(struct task_key *key, struct task_data *data, int task_bin_map_fd)
{
    int ret;
    struct task_bin bin = {0};

    ret = bpf_map_lookup_elem(task_bin_map_fd, key, &bin);
    if (ret == 0 && (data->base.task_status == TASK_STATUS_INVALID)) {
        // delete task bin entry, if task is invalid.
        (void)bpf_map_delete_elem(task_bin_map_fd, key);
    } else if ((ret != 0 ) && (data->base.task_status != TASK_STATUS_INVALID)) {
        // create new task bin entry, if new task entry finded.
        (void)bpf_map_update_elem(task_bin_map_fd, key, &bin, BPF_ANY);
    } else {
        ; // nothing to do.
    }
    return;
}

static void pull_probe_data(int task_map_fd, int task_bin_map_fd)
{
    int ret;
    struct task_key key = {0};
    struct task_key next_key = {0};
    struct task_data data;

    while (bpf_map_get_next_key(task_map_fd, &key, &next_key) != -1) {
        ret = bpf_map_lookup_elem(task_map_fd, &next_key, &data);
        if (ret == 0) {
            /* update task bin */
            update_task_bin_map(&next_key, &data, task_bin_map_fd);
        }

        if ((ret == 0) && (data.base.task_status == TASK_STATUS_INVALID)) {
            // delete hash record
            (void)bpf_map_delete_elem(task_map_fd, &next_key);
        } else {
            key = next_key;
        }
    }
    return;
}

static inline void u642addr(__u64 addr, char *buf, size_t s)
{
    buf[0] = 0;
    (void)snprintf(buf, s, "0x%llx", addr);
}

static void print_thread_metrics(struct task_data *value)
{
    char comm[MAX_PROCESS_NAME_LEN];
    char addr_str[MAX_PROCESS_NAME_LEN];

    (void)get_task_comm(value->id.tgid, comm, MAX_PROCESS_NAME_LEN);
    u642addr(value->net.kfree_skb_ret_addr, addr_str, MAX_PROCESS_NAME_LEN);

    fprintf(stdout,
            "|%s|%d|%d|%s|%d|%d|%u|%llu|%llu|%u|%llu|%llu|%s|\n",
            OO_THREAD_NAME,
            value->id.pid,
            value->id.tgid,
            comm,
            value->io.t_io_data.major,
            value->io.t_io_data.minor,
            value->base.fork_count,
            value->io.t_io_data.task_io_count,
            value->io.t_io_data.task_io_time_us,
            value->io.t_io_data.task_hang_count,
            value->io.t_io_data.task_io_wait_time_us,
            value->net.kfree_skb_cnt,
            addr_str);
}

static void print_process_metrics(struct task_data *value, int task_bin_map_fd)
{
    struct task_key key = {.tgid = value->id.tgid};
    struct task_bin bin = {0};

    // process bin info (comm / exec_file / exe_file)
    (void)bpf_map_lookup_elem(task_bin_map_fd, &key, &bin);
    get_task_bin_data(g_task_bin_map_fd, &bin, &key);
    // process io info
    (void)get_task_io(&(value->io.p_io_data), key.pid);
    // outout
    fprintf(stdout,
            "|%s|%d|%d|%s|%s|%s|%u|%llu|%llu|%u|%u|%llu|%llu|%llu|\n",
            OO_PROCESS_NAME,
            value->id.tgid,
            value->id.pgid,
            bin.comm,
            bin.exe_file,
            bin.exec_file,
            value->base.fork_count,
            value->io.p_io_data.task_rchar_bytes,
            value->io.p_io_data.task_wchar_bytes,
            value->io.p_io_data.task_syscr_count,
            value->io.p_io_data.task_syscw_count,
            value->io.p_io_data.task_read_bytes,
            value->io.p_io_data.task_write_bytes,
            value->io.p_io_data.task_cancelled_write_bytes);
}

static void print_task_metrics(int task_map_fd, int task_bin_map_fd)
{
    int ret;
    struct task_key ckey = {0};
    struct task_key nkey = {0};
    struct task_data data;

    while (bpf_map_get_next_key(task_map_fd, &ckey, &nkey) != -1) {
        ret = bpf_map_lookup_elem(task_map_fd, &nkey, &data);
        if (ret != 0) {
            ckey = nkey;
            continue;
        }
        print_thread_metrics(&data);
        if (data.id.pid == data.id.tgid && data.id.pgid != 0) {
            print_process_metrics(&data, task_bin_map_fd);
        }

        ckey = nkey;
    }
    (void)fflush(stdout);
    return;
}

int main(int argc, char **argv)
{
    int ret = -1;
    int pmap_fd, task_map_fd, task_bin_map_fd;

    if (signal(SIGINT, sig_int) == SIG_ERR) {
        fprintf(stderr, "can't set signal handler: %s\n", strerror(errno));
        return -1;
    }

    ret = args_parse(argc, argv, &tp_params);
    if (ret != 0) {
        return ret;
    }

    if (strlen(tp_params.task_whitelist) == 0) {
        fprintf(stderr, "***task_whitelist_path is null, please check param : -c xx/xxx *** \n");
    }
    DEBUG("Task probe starts with period: %us.\n", tp_params.period);

    INIT_BPF_APP(taskprobe, EBPF_RLIM_LIMITED);

    LOAD(taskprobe, err3);
    LOAD(thread_io, err2);
    LOAD(process_io, err1);
    LOAD(taskprobe_net, err);

    pmap_fd = GET_MAP_FD(taskprobe, probe_proc_map);
    task_map_fd = GET_MAP_FD(taskprobe, __task_map);
    task_bin_map_fd = GET_MAP_FD(taskprobe, task_bin_map);

    load_task_range(pmap_fd);

    load_task_wl(pmap_fd);

    load_daemon_task(pmap_fd, task_map_fd);

    printf("Successfully started!\n");

    while (stop == 0) {
        pull_probe_data(task_map_fd, task_bin_map_fd);
        print_task_metrics(task_map_fd, task_bin_map_fd);
        sleep(tp_params.period);
    }

err:
    UNLOAD(taskprobe_net);
err1:
    UNLOAD(process_io);
err2:
    UNLOAD(thread_io);
err3:
    UNLOAD(taskprobe);
    return ret;
}
