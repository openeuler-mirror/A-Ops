/******************************************************************************
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 * gala-gopher licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Author: wo_cow
 * Create: 2022-7-29
 * Description: opengauss_sli probe user prog
 ******************************************************************************/
#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <pthread.h>

#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif

#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif

#include "bpf.h"
#include "args.h"
#include "hash.h"
#include "opengauss_sli.skel.h"
#include "tc_loader.h"
#include "container.h"
#include "opengauss_sli.h"

#define SLI_TBL_NAME "opengauss_sli"
#define GUASSDB_COMM "gaussdb"
#define PLDD_LIBSSL_COMMAND "pldd %u | grep libssl"
#define PID_COMM_COMMAND "ps -e -o pid,comm | grep %s | awk '{print $1}'"

#define R_OK    4

static volatile sig_atomic_t stop;
static struct probe_params params = {.period = DEFAULT_PERIOD};
static struct bpf_link_hash_t *head = NULL;

enum pid_state_t {
    PID_NOEXIST,
    PID_ELF_TOBE_ATTACHED,
    PID_ELF_ATTACHED
};

struct bpf_link_hash_value {
    enum pid_state_t pid_state;
    char elf_path[MAX_PATH_LEN];
    struct bpf_link *bpf_link_read;
    struct bpf_link *bpf_link_read_ret;
    struct bpf_link *bpf_link_write;
    struct bpf_link *bpf_link_shudown;
};

struct bpf_link_hash_t {
    H_HANDLE;
    unsigned int pid; // key
    struct bpf_link_hash_value v; // value
};

static void sig_int(int signo)
{
    stop = 1;
}

static void msg_event_handler(void *ctx, int cpu, void *data, unsigned int size)
{
    struct msg_event_data_t *msg_evt_data = (struct msg_event_data_t *)data;
    fprintf(stdout,
            "|%s|%u|%d|%s|%c|%c|%llu|\n",
            SLI_TBL_NAME,
            msg_evt_data->tgid,
            msg_evt_data->fd,
            "POSTGRE",
            msg_evt_data->req_cmd,
            msg_evt_data->rsp_cmd,
            msg_evt_data->rtt);
    (void)fflush(stdout);

    return;
}

static void *msg_event_receiver(void *arg)
{
    int fd = *(int *)arg;
    struct perf_buffer *pb;

    pb = create_pref_buffer(fd, msg_event_handler);
    if (pb == NULL) {
        fprintf(stderr, "Failed to create perf buffer.\n");
        stop = 1;
        return NULL;
    }

    poll_pb(pb, params.period * 1000);

    stop = 1;
    return NULL;
}

static int init_conn_mgt_process(int msg_evt_map_fd)
{
    int err;
    pthread_t msg_evt_hdl_thd;

    err = pthread_create(&msg_evt_hdl_thd, NULL, msg_event_receiver, (void *)&msg_evt_map_fd);
    if (err != 0) {
        fprintf(stderr, "Failed to create connection read/write message event handler thread.\n");
        return -1;
    }
    printf("Connection read/write message event handler thread successfully started!\n");

    return 0;
}

static void load_args(int args_fd, struct probe_params* params)
{
    __u32 key = 0;
    struct ogsli_args_s args = {0};

    args.period = NS(params->period);

    (void)bpf_map_update_elem(args_fd, &key, &args, BPF_ANY);
}


static struct bpf_link_hash_t* find_bpf_link(unsigned int pid)
{
    struct bpf_link_hash_t *item = NULL;

    if (head == NULL) {
        return NULL;
    }
    H_FIND(head, &pid, sizeof(unsigned int), item);
    if (item == NULL) {
        return NULL;
    }

    if (item->v.bpf_link_read == NULL) {
        item->v.pid_state = PID_ELF_TOBE_ATTACHED;
    } else {
        item->v.pid_state = PID_ELF_ATTACHED;
    }

    return item;
}

static int get_elf_path(unsigned int pid, char elf_path[], int max_path_len)
{
    char cmd[COMMAND_LEN] = {0};
    char openssl_path[PATH_LEN] = {0};
    char container_id[CONTAINER_ABBR_ID_LEN] = {0};
    char container_path[PATH_LEN] = {0};

    // 1. get elf_path
    (void)snprintf(cmd, COMMAND_LEN, PLDD_LIBSSL_COMMAND, pid);
    if (exec_cmd((const char *)cmd, openssl_path, PATH_LEN) < 0) {
        fprintf(stderr, "pldd %u grep libssl failed\n", pid);
        return SLI_ERR;
    }

    // If the container id is not found, it means that gaussdb is a process on the host
    if ((get_container_id_by_pid(pid, container_id, CONTAINER_ABBR_ID_LEN + 1) >= 0) &&
        (container_id[0] != 0)) {
        if (get_container_merged_path(container_id, container_path, PATH_LEN) < 0) {
            fprintf(stderr, "get container %s merged path failed\n", container_id);
            return SLI_ERR;
        }
        (void)snprintf(elf_path, max_path_len, "%s%s", container_path, openssl_path);
    } else {
        (void)snprintf(elf_path, max_path_len, "%s", openssl_path);
    }

    if (elf_path[0] != '\0') {
        if (access(elf_path, R_OK) != 0) {
            fprintf(stderr, "File %s not exist or not readable!\n", elf_path);
            return SLI_ERR;
        }
    }

    return SLI_OK;
}

static int add_bpf_link(unsigned int pidd)
{
    struct bpf_link_hash_t *item = malloc(sizeof(struct bpf_link_hash_t));
    if (item == NULL) {
        fprintf(stderr, "malloc bpf link %u failed\n", pidd);
        return SLI_ERR;
    }
    (void)memset(item, 0, sizeof(struct bpf_link_hash_t));
    if (get_elf_path(pidd, item->v.elf_path, MAX_PATH_LEN) != SLI_OK) {
        free(item);
        return SLI_ERR;
    }

    item->pid = pidd;
    item->v.pid_state = PID_ELF_TOBE_ATTACHED;
    H_ADD(head, pid, sizeof(unsigned int), item);

    return SLI_OK;
}

/*
[root@localhost ~]# ps -e -o pid,comm | grep gaussdb | awk '{print $1}'
*/
static int add_bpf_link_by_search_pids()
{
    unsigned int pid = 0;
    char cmd[COMMAND_LEN] = {0};
    char line[LINE_BUF_LEN] = {0};
    FILE *f;
    int ret = SLI_OK;

    (void)snprintf(cmd, COMMAND_LEN, PID_COMM_COMMAND, GUASSDB_COMM);
    f = popen(cmd, "r");
    if (f == NULL) {
        fprintf(stderr, "get pid of gaussdb failed.\n");
        return SLI_ERR;
    }

    // Traverse the gaussdb process to attach libssl
    while (!feof(f)) {
        line[0] = 0;
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            continue;
        }
        pid = (unsigned int)atoi(line);
        if (pid <= 0) {
            continue;
        }
        // find_bpf_link and add_bpf_link will set bpf_link status
        if (!find_bpf_link(pid)) {
            if (add_bpf_link(pid) != SLI_OK) {
                fprintf(stderr, "add_bpf_link of pid %u failed\n", pid);
            } else {
                printf("add_bpf_link of pid %u success\n", pid);
            }
        }
    }

    (void)pclose(f);
    return ret;
}

static void set_bpf_link_inactive()
{
    struct bpf_link_hash_t *item, *tmp;
    if (head == NULL) {
        return;
    }
    
    H_ITER(head, item, tmp) {
        item->v.pid_state = PID_NOEXIST;
    }
}

static void clear_invalid_bpf_link()
{
    struct bpf_link_hash_t *item, *tmp;
    if (head == NULL) {
        return;
    }
    H_ITER(head, item, tmp) {
        if (item->v.pid_state == PID_NOEXIST) {
            printf("clear bpf link of pid %u\n", item->pid);
            H_DEL(head, item);
            (void)free(item);
        }
    }
}

static void clear_all_bpf_link()
{
    struct bpf_link_hash_t *item, *tmp;
    if (head == NULL) {
        return;
    }
    H_ITER(head, item, tmp) {
        UNATTACH_ONELINK(opengauss_sli, item->v.bpf_link_read);
        UNATTACH_ONELINK(opengauss_sli, item->v.bpf_link_read_ret);
        UNATTACH_ONELINK(opengauss_sli, item->v.bpf_link_write);
        UNATTACH_ONELINK(opengauss_sli, item->v.bpf_link_shudown);
        H_DEL(head, item);
        (void)free(item);
    }
}

int main(int argc, char **argv)
{
    int err, ret;
    int init = 0;
    struct bpf_link_hash_t *item, *tmp;

    err = args_parse(argc, argv, &params);
    if (err != 0) {
        return -1;
    }
    printf("arg parse interval time:%us\n", params.period);

    INIT_BPF_APP(opengauss_sli, EBPF_RLIM_LIMITED);
    LOAD(opengauss_sli, init_err);

    if (signal(SIGINT, sig_int) == SIG_ERR) {
        fprintf(stderr, "Can't set signal handler: %d\n", errno);
        goto init_err;
    }

    printf("opengauss_sli probe successfully started!\n");

    while (!stop) {
        set_bpf_link_inactive();
        if (add_bpf_link_by_search_pids() != SLI_OK) {
            goto init_err;
        }

        // attach to libssl
        H_ITER(head, item, tmp) {
            if (item->v.pid_state == PID_ELF_TOBE_ATTACHED) {
                UBPF_ATTACH_ONELINK(opengauss_sli, SSL_read, item->v.elf_path, SSL_read,
                    item->v.bpf_link_read, ret);
                if (ret <= 0) {
                    fprintf(stderr, "Can't attach function SSL_read at elf_path %s.\n", item->v.elf_path);
                    goto init_err;
                }
                UBPF_RET_ATTACH_ONELINK(opengauss_sli, SSL_read, item->v.elf_path, SSL_read,
                    item->v.bpf_link_read_ret, ret);
                if (ret <= 0) {
                    fprintf(stderr, "Can't attach ret function SSL_read at elf_path %s.\n", item->v.elf_path);
                    goto init_err;
                }
                UBPF_ATTACH_ONELINK(opengauss_sli, SSL_write, item->v.elf_path, SSL_write,
                    item->v.bpf_link_write, ret);
                if (ret <= 0) {
                    fprintf(stderr, "Can't attach function SSL_write at elf_path %s.\n", item->v.elf_path);
                    goto init_err;
                }
                UBPF_ATTACH_ONELINK(opengauss_sli, SSL_shutdown, item->v.elf_path, SSL_shutdown,
                    item->v.bpf_link_shudown, ret);
                if (ret <= 0) {
                    fprintf(stderr, "Can't attach function SSL_shutdown at elf_path %s.\n", item->v.elf_path);
                    goto init_err;
                }
                item->v.pid_state = PID_ELF_ATTACHED;
            }
        }

        clear_invalid_bpf_link();
        if (init == 0) {
            load_args(GET_MAP_FD(opengauss_sli, args_map), &params);
            err = init_conn_mgt_process(GET_MAP_FD(opengauss_sli, msg_event_map));
            if (err != 0) {
                fprintf(stderr, "Init connection management process failed.\n");
                goto init_err;
            }
            init = 1;
        }
        sleep(params.period);
    }

init_err:
    clear_all_bpf_link();
    UNLOAD(opengauss_sli);
    return -err;
}