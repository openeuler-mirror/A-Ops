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
#include "task.h"
#include "taskprobe.h"

#define TASK_PROBE_IO_PATH "cat /proc/%d/io"
#define TASK_PROBE_STAT_PATH "cat /proc/%d/stat"
#define TASK_PROBE_SMAPS_PATH "cat /proc/%d/smaps"
#define PROCESS_STATUS_COMMAND \
    "ps -eo pid,ppid,pgid,comm | grep -w \"%s\" | awk '{print $1 \"|\" $2 \"|\" $3 \"|\" $4}'"
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

static int is_existed_process(const char *comm)
{
    FILE *f = NULL;
    char cmd[COMMAND_LEN] = {0};
    char line[LINE_BUF_LEN] = {0};

    (void)snprintf(cmd, COMMAND_LEN, PROCESS_STATUS_COMMAND, comm);
    f = popen(cmd, "r");
    if (f == NULL) {
        return -1;
    }
    if (fgets(line, LINE_BUF_LEN, f) == NULL) {
        printf("process %s is not existed.\n", comm);
        return -1;
    }
    (void)pclose(f);
    return 0;
}

/* ps_rlt exemple:
    ps -eo pid,ppid,pgid,comm | grep nginx | awk '{print $1 "|" $2 "|" $3 "|" $4}'
    3144599|3144598|3144598|nginx
    3144600|3144598|3144598|nginx
 */
static int parse_ps_result(const char *ps_rlt, struct task_key *k, struct task_data *d)
{
    int i;
    int start = 0, j = 0;
    char id_str[PS_TYPE_MAX][TASK_COMM_LEN] = {0};
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
    d->tgid = k->pid;
    d->ppid = (unsigned int)atoi(id_str[PS_TYPE_PPID]);
    d->pgid = (unsigned int)atoi(id_str[PS_TYPE_PGID]);
    (void)strncpy((char *)id_str[j], ps_rlt + start, len - start);
    (void)strcpy((char *)d->comm, (char *)id_str[j]);

    return 0;
}

static int add_process_infos(const char *comm, int map_fd)
{
    FILE *f = NULL;
    char cmd[COMMAND_LEN] = {0};
    char line[LINE_BUF_LEN] = {0};
    struct task_key key = {0};
    struct task_data kdata = {0};
    int ret = 0;

    (void)snprintf(cmd, COMMAND_LEN, PROCESS_STATUS_COMMAND, comm);
    f = popen(cmd, "r");
    if (f == NULL) {
        return -1;
    }
    while (!feof(f)) {
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            break;
        }
        __SPLIT_NEWLINE_SYMBOL(line);
        if (parse_ps_result((char *)line, &key, &kdata) < 0) {
            ret = -1;
            goto out;
        }
        /* update task_map */
        bpf_map_update_elem(map_fd, &key, &kdata, BPF_ANY);
    }
out:
    pclose(f);
    return ret;
}

static int update_existed_task_to_map(int p_fd, int map_fd)
{
    struct probe_process ckey = {0};
    struct probe_process nkey = {0};
    int flag;
    int ret = -1;

    while (bpf_map_get_next_key(p_fd, &ckey, &nkey) != -1) {
        ret = bpf_map_lookup_elem(p_fd, &nkey, &flag);
        if (ret == 0) {
            /* check whether process existed, if it is, add process to task_map */
            if (is_existed_process((char *)nkey.name) >= 0) {
                /* add other info of process */
                if (add_process_infos((char *)nkey.name, map_fd) < 0) {
            		printf("add process info fail.\n");
                    return -1;
                }
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
        memset(pname.name, 0, MAX_PROCESS_NAME_LEN);
        strcpy(pname.name, default_probed_process_list[i]);
        /* update task_map */
        bpf_map_update_elem(p_fd, &pname, &flag, BPF_ANY);
    }
    return 0;
}

int jinfo_get_label_info(int pid, char *label, char *buf, int buf_len)
{
    FILE *f = NULL;
    char command[COMMAND_LEN] = {0};
    char line[LINE_BUF_LEN] = {0};
    char *colon = NULL;
    int len = (buf_len <= LINE_BUF_LEN) ? buf_len : LINE_BUF_LEN;

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
    memset(java_command, 0, JAVA_COMMAND_LEN);
    if (jinfo_get_label_info(pid, TASK_PROBE_JAVA_COMMAND, java_command, JAVA_COMMAND_LEN) < 0) {
        printf("java process get command fail.\n");
        return -1;
    }
    memset(java_classpath, 0, JAVA_CLASSPATH_LEN);
    if (jinfo_get_label_info(pid, TASK_PROBE_JAVA_CLASSPATH, java_classpath, JAVA_CLASSPATH_LEN) < 0) {
        printf("java process get command fail.\n");
        return -1;
    }
    return 0;
}

static void task_probe_pull_probe_data(int map_fd)
{
    int ret;
    struct task_key ckey = {0};
    struct task_key nkey = {0};
    struct task_data tkd;
    char java_command[JAVA_COMMAND_LEN] = {0};
    char java_classpath[JAVA_CLASSPATH_LEN] = {0};

    while (bpf_map_get_next_key(map_fd, &ckey, &nkey) != -1) {
        ret = bpf_map_lookup_elem(map_fd, &nkey, &tkd);
        	if (ret != 0) {
        	continue;
    	}
    	/* exec file name */
        if (strlen(tkd.exe_file) == 0) {
            get_task_exe(nkey.pid, &tkd.exe_file, TASK_EXE_FILE_LEN);
        }
		
    	if (strstr(tkd.comm, "java") != NULL) {
            /* java */
            (void)update_java_process_info(nkey.pid, (char *)java_command, (char *)java_classpath);
        } else if (strstr(tkd.comm, "python") != NULL || strstr(tkd.comm, "go") != NULL) {
            /* python/go run */
            (void)get_task_pwd(nkey.pid, (char *)tkd.exec_file);
        } else {
            /* c/c++/go */
            strcpy((char *)tkd.exec_file, (char *)tkd.exe_file);
        }

        fprintf(stdout, "|%s|%d|%d|%d|%s|%s|%s|%s|%d\n",
            OO_NAME_TASK,
            tkd.tgid,
            nkey.pid,
            tkd.pgid,
            tkd.comm,
            tkd.exe_file,
            strlen(tkd.exec_file) == 0 ? java_command : tkd.exec_file,
            java_classpath,
            tkd.fork_count
        );

	    DEBUG("tgid[%d] pid[%d] ppid[%d] pgid[%d] comm[%s] exe_file[%s] exec_file[%s] fork_count[%d] java_classpath[%s] \n",
	            tkd.tgid,
	            nkey.pid,
	            tkd.ppid,
	            tkd.pgid,
	            tkd.comm,
	            tkd.exe_file,
	            strlen(tkd.exec_file) == 0 ? java_command : tkd.exec_file,
	        	tkd.fork_count,
	            java_classpath
	        );
    	ckey = nkey;
    }

    return;
}

int main(int argc, char **argv)
{
    int ret = -1;
    int pmap_fd = -1;
    int taskmap_fd = -1;

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

    remove(TASK_EXIT_MAP_FILE_PATH);
    ret = bpf_obj_pin(GET_MAP_FD(task_exit_event), TASK_EXIT_MAP_FILE_PATH);
    if (ret != 0) {
        fprintf(stderr, "Failed to pin exit task map: %d\n", errno);
        goto err;
    }
    printf("Exit task map pin success.\n");

    pmap_fd = bpf_map__fd(skel->maps.probe_proc_map);
    taskmap_fd = bpf_map__fd(skel->maps.task_map);

    ret = update_default_probed_process_to_map(pmap_fd);
    if (ret != 0) {
        fprintf(stderr, "Failed to update default probe proc info to probe_process map. \n");
        goto err;
    }

    ret = update_existed_task_to_map(pmap_fd, taskmap_fd);
    if (ret != 0) {
        fprintf(stderr, "Failed to update existed proc to task map. \n");
        goto err;
    }

    while (stop == 0) {
        task_probe_pull_probe_data(taskmap_fd);
        sleep(tp_params.period);
    }

    ret = remove(TASK_EXIT_MAP_FILE_PATH);
    if (!ret) {
        printf("Pinned file:(%s) of task exit map removed.\n", TASK_EXIT_MAP_FILE_PATH);
    } else {
        fprintf(stderr, "Failed to remove pinned file:(%s) of task exit map.", TASK_EXIT_MAP_FILE_PATH);
    }

err:
    UNLOAD(taskprobe);
    return ret;
}
