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
#include "taskprobe_io.skel.h"
#include "taskprobe_net.skel.h"
#include "taskprobe.h"

#define TASK_COMM "/proc/%d/comm"
#define TASK_CWD_FILE "/proc/%d/cwd"
#define TASK_EXE_FILE "/proc/%d/exe"

#define TASK_PROBE_JAVA_COMMAND "sun.java.command"
#define TASK_PROBE_JAVA_CLASSPATH "java.class.path"
#define OO_NAME_TASK "task"

#define TASK_PROBE_COLLECTION_PERIOD 5

enum task_type_e {
    TASK_TYPE_APP = 0,
    TASK_TYPE_KERN,
    TASK_TYPE_OS
};

struct task_name_t {
    char name[MAX_PROCESS_NAME_LEN];
    enum task_type_e type;
};

static volatile sig_atomic_t stop = 0;
static struct probe_params tp_params = {.period = TASK_PROBE_COLLECTION_PERIOD,
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

int jinfo_get_label_info(int pid, char *label, char *buf, int buf_len)
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

int update_java_process_info(int pid, char *java_command, char *java_classpath)
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

static void update_task_bin_map(struct task_key *key, struct task_data *data, 
                                                    int task_bin_map_fd)
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
            (void)bpf_map_delete_elem(task_map_fd, &next_key);
        } else {
            key = next_key;
        }
    }
    return;
}

static void get_task_bin_data(int bin_fd, struct task_bin* bin, struct task_key* key)
{
    char java_command[JAVA_COMMAND_LEN];
    char java_classpath[JAVA_CLASSPATH_LEN];

    if (bin->comm[0] == 0) {
        (void)get_task_comm(key->pid, bin->comm, TASK_COMM_LEN);
    }

    /* exe file name */
    if (bin->exe_file[0] == 0) {
        (void)get_task_exe(key->pid, bin->exe_file, TASK_EXE_FILE_LEN);
    }

    /* exec file name */
    if (strstr(bin->comm, "java") != NULL && bin->exec_file[0] == 0) {
        /* java */
        (void)update_java_process_info(key->pid, (char *)java_command, (char *)java_classpath);
        (void)strncpy(bin->exec_file, java_command, TASK_EXE_FILE_LEN);
    } else if (strstr(bin->comm, "python") != NULL || strstr(bin->comm, "go") != NULL) {
        /* python/go run */
        (void)get_task_cwd(key->pid, bin->exec_file, TASK_EXE_FILE_LEN);
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

#define ADDR_STR_LEN 32
static inline void u642addr(__u64 addr, char *buf, size_t s)
{
    buf[0] = 0;
    (void)snprintf(buf, s, "0x%llx", addr);
}

int get_task_io(struct task_io_data *io_data, int pid);

static void task_probe_pull_probe_data(int task_map_fd, int task_bin_map_fd)
{
    int ret;
    struct task_key ckey = {0};
    struct task_key nkey = {0};
    struct task_data data;
    struct task_bin bin;
    char addr_str[ADDR_STR_LEN];

    while (bpf_map_get_next_key(task_map_fd, &ckey, &nkey) != -1) {
        ret = bpf_map_lookup_elem(task_map_fd, &nkey, &data);
        if (ret != 0) {
            ckey = nkey;
            continue;
        }

        ret = bpf_map_lookup_elem(task_bin_map_fd, &nkey, &bin);
        if (ret != 0) {
            ckey = nkey;
            continue;
        }

        get_task_bin_data(task_bin_map_fd, &bin, &nkey);
        (void)get_task_io(&data.io, nkey.pid);

        u642addr(data.net.kfree_skb_ret_addr, addr_str, ADDR_STR_LEN);
        
        fprintf(stdout, "|%s|%d|%d|%d|%s|%s|%s|%d|%d|%d|%llu|%llu|%llu|%llu|%llu|%u|%u|%llu|%llu|%llu|%u|%llu|%s|\n",
                OO_NAME_TASK,
                data.id.tgid,
                nkey.pid,
                data.id.pgid,
                bin.comm,
                bin.exe_file,
                bin.exec_file,
                data.base.fork_count,
                data.io.major,
                data.io.minor,
                data.io.task_io_wait_time_us,
                data.io.task_io_count,
                data.io.task_io_time_us,
                data.io.task_rchar_bytes,
                data.io.task_wchar_bytes,
                data.io.task_syscr_count,
                data.io.task_syscw_count,
                data.io.task_read_bytes,
                data.io.task_write_bytes,
                data.io.task_cancelled_write_bytes,
                data.io.task_hang_count,
                data.net.kfree_skb_cnt,
                addr_str);

        DEBUG("tgid[%d] pid[%d] ppid[%d] pgid[%d] comm[%s] exe_file[%s] exec_file[%s] fork_count[%d] major[%d] minor[%d] "
                "iowait[%llu] iocount[%llu] iotime[%llu] rchar[%llu] wchar[%llu] sysr[%u] sysw[%u] rbytes[%llu] wbytes[%llu] "
                "cancelbytes[%llu] hang[%u] skb_free[%llu] addr[%s]\n",
                data.id.tgid,
                nkey.pid,
                data.id.ppid,
                data.id.pgid,
                bin.comm,
                bin.exe_file,
                bin.exec_file,
                data.base.fork_count,
                data.io.major,
                data.io.minor,
                data.io.task_io_wait_time_us,
                data.io.task_io_count,
                data.io.task_io_time_us,
                data.io.task_rchar_bytes,
                data.io.task_wchar_bytes,
                data.io.task_syscr_count,
                data.io.task_syscw_count,
                data.io.task_read_bytes,
                data.io.task_write_bytes,
                data.io.task_cancelled_write_bytes,
                data.io.task_hang_count,
                data.net.kfree_skb_cnt,
                addr_str);

        ckey = nkey;
    }

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

    ret = args_parse(argc, argv, "t:w:", &tp_params);
    if (ret != 0)
        return ret;

    if (strlen(tp_params.task_whitelist) == 0) {
        fprintf(stderr, "***task_whitelist_path is null, please check param : -c xx/xxx *** \n");
    }

    DEBUG("Task probe starts with period: %us.\n", tp_params.period);

    INIT_BPF_APP(taskprobe);

    LOAD(taskprobe, err3);
    LOAD(taskprobe_io, err2);
    LOAD(taskprobe_net, err);

    pmap_fd = GET_MAP_FD(taskprobe, probe_proc_map);
    task_map_fd = GET_MAP_FD(taskprobe, __task_map);
    task_bin_map_fd = GET_MAP_FD(taskprobe, task_bin_map);

    load_task_range(pmap_fd);

    load_task_wl(pmap_fd);

    load_daemon_task(pmap_fd, task_map_fd);

    while (stop == 0) {
        pull_probe_data(task_map_fd, task_bin_map_fd);
        task_probe_pull_probe_data(task_map_fd, task_bin_map_fd);
        sleep(tp_params.period);
    }

err:
    UNLOAD(taskprobe_net);
err2:
    UNLOAD(taskprobe_io);
err3:
    UNLOAD(taskprobe);
    return ret;
}
