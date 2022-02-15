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
#include "taskprobe.h"

#define ERR_MSG "No such file or directory"

#define TASK_PROBE_IO_PATH "cat /proc/%d/io"
#define TASK_PROBE_STAT_PATH "cat /proc/%d/stat"
#define TASK_PROBE_SMAPS_PATH "cat /proc/%d/smaps"

#define TASK_COMM_COMMAND "/usr/bin/cat /proc/%d/comm"

#define TASK_ID_COMMAND \
    "ps -eo pid,ppid,pgid,comm | grep -w \"%s\" | awk '{print $1 \"|\" $2 \"|\" $3}'"
#define TASK_PROBE_JAVA_COMMAND "sun.java.command"
#define TASK_PROBE_JAVA_CLASSPATH "java.class.path"
#define OO_NAME_TASK "task"

#define TASK_PROBE_COLLECTION_PERIOD 5

#define __SPLIT_NEWLINE_SYMBOL(s) \
    do { \
        int __len = strlen(s); \
        if (__len > 0 && (s)[__len - 1] == '\n') { \
            (s)[__len - 1] = 0; \
        } \
    } while (0)

static volatile sig_atomic_t stop = 0;
static struct probe_params tp_params = {.period = TASK_PROBE_COLLECTION_PERIOD};

static int default_probed_process_num = 6;
static char default_probed_process_list[10][MAX_PROCESS_NAME_LEN] = {
    "go",
    "java",
    "python",
    "python3",
    "nginx",
    "gala-gopher"
};

static void sig_int(int signal)
{
    stop = 1;
}

static int get_task_comm(int pid, char *buf, unsigned int buf_len)
{
    char cmd[COMMAND_LEN];
    char line[LINE_BUF_LEN];
    FILE *f = NULL;

    cmd[0] = 0;
    line[0] = 0;
    (void)snprintf(cmd, COMMAND_LEN, TASK_COMM_COMMAND, pid);
    f = popen(cmd, "r");
    if (f == NULL) {
        return -1;
    }
    if (fgets(line, LINE_BUF_LEN, f) == NULL) {
        (void)pclose(f);
        return -1;
    }
    if (strstr(line, ERR_MSG) != NULL) {
        (void)pclose(f);
        return -1;
    }
    __SPLIT_NEWLINE_SYMBOL(line);
    (void)strncpy(buf, line, buf_len);
    return 0;
}


/* ps_rlt exemple:
    ps -eo pid,ppid,pgid,comm | grep nginx | awk '{print $1 "|" $2 "|" $3 "|" $4}'
    3144599|3144598|3144598
    3144600|3144598|3144598
 */
static int do_get_daemon_task_id(const char *ps_rlt, struct task_key *k, struct task_data *data)
{
    int i;
    int start = 0, j = 0;
    char id_str[PS_TYPE_MAX][INT_LEN] = {0};
    int len = strlen(ps_rlt);

    for (i = 0; i < len; i++) {
        if (ps_rlt[i] == '|') {
            (void)strncpy(id_str[j++], ps_rlt + start, i - start);
            start = i + 1;
        }
    }
    if (j != PS_TYPE_MAX - 1) {
        return -1;
    }

    k->pid = (unsigned int)atoi(id_str[PS_TYPE_PID]);
    data->id.tgid = k->pid;
    data->id.ppid = (unsigned int)atoi(id_str[PS_TYPE_PPID]);
    data->id.pgid = (unsigned int)atoi(id_str[PS_TYPE_PGID]);

    return 0;
}

static int get_daemon_task_id(const char *comm, int task_map_fd)
{
    FILE *f = NULL;
    char cmd[COMMAND_LEN] = {0};
    char line[LINE_BUF_LEN] = {0};
    struct task_key key = {0};
    struct task_data data = {0};
    int ret = 0;

    (void)snprintf(cmd, COMMAND_LEN, TASK_ID_COMMAND, comm);
    f = popen(cmd, "r");
    if (f == NULL) {
        return -1;
    }
    while (!feof(f)) {
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            break;
        }
        __SPLIT_NEWLINE_SYMBOL(line);
        if (do_get_daemon_task_id((char *)line, &key, &data) < 0) {
            ret = -1;
            goto out;
        }
        /* update damemon task map */
        (void)bpf_map_update_elem(task_map_fd, &key, &data, BPF_ANY);
    }
out:
    pclose(f);
    return ret;
}

static int get_daemon_task(int p_fd, int task_map_fd)
{
    struct probe_process ckey = {0};
    struct probe_process nkey = {0};
    int flag;
    int ret = -1;

    while (bpf_map_get_next_key(p_fd, &ckey, &nkey) != -1) {
        ret = bpf_map_lookup_elem(p_fd, &nkey, &flag);
        if (ret == 0) {
            if (get_daemon_task_id((char *)nkey.name, task_map_fd) < 0) {
                printf("add process info fail.\n");
                return -1;
            }
        }
        ckey = nkey;
    }

    return 0;
}

static int update_default_probed_process_to_map(int p_fd)
{
    struct probe_process pname;
    int flag = 1;

    for (int i = 0; i < default_probed_process_num; i++) {
        (void)memset(pname.name, 0, MAX_PROCESS_NAME_LEN);
        (void)strcpy(pname.name, default_probed_process_list[i]);
        /* update task_map */
        (void)bpf_map_update_elem(p_fd, &pname, &flag, BPF_ANY);
    }
    return 0;
}

int jinfo_get_label_info(int pid, char *label, char *buf, int buf_len)
{
    FILE *f = NULL;
    char command[COMMAND_LEN];
    char line[LINE_BUF_LEN];
    char *colon = NULL;
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
    __SPLIT_NEWLINE_SYMBOL(line);
    (void)strncpy(buf, line, len - 1);

    (void)pclose(f);
    return 0;
}

int update_java_process_info(int pid, char *java_command, char *java_classpath)
{
    java_command[0] = 0;
    if (jinfo_get_label_info(pid, TASK_PROBE_JAVA_COMMAND, java_command, JAVA_COMMAND_LEN) < 0) {
        printf("java process get command fail.\n");
        return -1;
    }
    java_classpath[0] = 0;
    if (jinfo_get_label_info(pid, TASK_PROBE_JAVA_CLASSPATH, java_classpath, JAVA_CLASSPATH_LEN) < 0) {
        printf("java process get command fail.\n");
        return -1;
    }
    return 0;
}

static int create_task_bin_tbl()
{
    int fd;
    /* create bin hs map */
    fd = bpf_create_map(BPF_MAP_TYPE_HASH, sizeof(struct task_key), \
            sizeof(struct task_bin), SHARE_MAP_TASK_MAX_ENTRIES, 0);
    if (fd < 0) {
        fprintf(stderr, "create_task_bin_tbl create failed.\n");
        return -1;
    }
    return fd;
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

static void get_task_bin_data(struct task_bin* bin, int pid)
{
    char java_command[JAVA_COMMAND_LEN];
    char java_classpath[JAVA_CLASSPATH_LEN];

    if (bin->comm[0] == 0) {
        (void)get_task_comm(pid, bin->comm, TASK_COMM_LEN);
    }
    
    /* exe file name */
    if (bin->exe_file[0] == 0) {
        get_task_exe(pid, &bin->exe_file, TASK_EXE_FILE_LEN);
    }

    /* exec file name */
    if (strstr(bin->comm, "java") != NULL && bin->exec_file[0] == 0) {
        /* java */
        (void)update_java_process_info(pid, (char *)java_command, (char *)java_classpath);
        (void)strncpy(bin->exec_file, java_command, TASK_EXE_FILE_LEN);
    } else if (strstr(bin->comm, "python") != NULL || strstr(bin->comm, "go") != NULL) {
        /* python/go run */
        (void)get_task_pwd(pid, (char *)bin->exec_file);
    } else if (bin->exec_file[0] == 0) {
        /* c/c++/go */
        (void)strncpy((char *)bin->exec_file, (char *)bin->exe_file, TASK_EXE_FILE_LEN);
    } else {
        ; // nothing to do.
    }
    return;
}

static void task_probe_pull_probe_data(int task_map_fd, int task_bin_map_fd)
{
    int ret;
    struct task_key ckey = {0};
    struct task_key nkey = {0};
    struct task_data data;
    struct task_bin bin;

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

        get_task_bin_data(&bin, nkey.pid);
        
        fprintf(stdout, "|%s|%d|%d|%d|%s|%s|%s|%d\n",
                OO_NAME_TASK,
                data.id.tgid,
                nkey.pid,
                data.id.pgid,
                bin.comm,
                bin.exe_file,
                bin.exec_file,
                data.base.fork_count);

        DEBUG("tgid[%d] pid[%d] ppid[%d] pgid[%d] comm[%s] exe_file[%s] exec_file[%s] fork_count[%d]\n",
                data.id.tgid,
                nkey.pid,
                data.id.ppid,
                data.id.pgid,
                bin.comm,
                bin.exe_file,
                bin.exec_file,
                data.base.fork_count);

        ckey = nkey;
    }

    return;
}

int main(int argc, char **argv)
{
    int ret = -1;
    int pmap_fd = -1;
    int task_map_fd = -1;
    int task_bin_map_fd = -1;

    ret = signal(SIGINT, sig_int);
    if (ret < 0) {
        printf("Can't set signal handler: %d\n", errno);
        goto err;
    }

    ret = args_parse(argc, argv, "t:", &tp_params);
    if (ret != 0)
        return ret;

    printf("Task probe starts with period: %us.\n", tp_params.period);

    LOAD(taskprobe);

    /*
    remove(TASK_EXIT_MAP_FILE_PATH);
    ret = bpf_obj_pin(GET_MAP_FD(task_exit_event), TASK_EXIT_MAP_FILE_PATH);
    if (ret != 0) {
        fprintf(stderr, "Failed to pin exit task map: %d\n", errno);
        goto err;
    }
    printf("Exit task map pin success.\n");
    */

    pmap_fd = GET_MAP_FD(probe_proc_map);
    task_map_fd = GET_MAP_FD(__task_map);
    task_bin_map_fd = create_task_bin_tbl();
    if (task_bin_map_fd < 0) {
        goto err;
    }

    ret = update_default_probed_process_to_map(pmap_fd);
    if (ret != 0) {
        fprintf(stderr, "Failed to update default probe proc info to probe_process map. \n");
        goto err;
    }

    ret = get_daemon_task(pmap_fd, task_map_fd);
    if (ret != 0) {
        fprintf(stderr, "Failed to update existed proc to task map. \n");
        goto err;
    }

    while (stop == 0) {
        pull_probe_data(task_map_fd, task_bin_map_fd);
        task_probe_pull_probe_data(task_map_fd, task_bin_map_fd);
        sleep(tp_params.period);
    }

    /*
    ret = remove(TASK_EXIT_MAP_FILE_PATH);
    if (!ret) {
        printf("Pinned file:(%s) of task exit map removed.\n", TASK_EXIT_MAP_FILE_PATH);
    } else {
        fprintf(stderr, "Failed to remove pinned file:(%s) of task exit map.", TASK_EXIT_MAP_FILE_PATH);
    }
    */

err:
    UNLOAD(taskprobe);
    return ret;
}
