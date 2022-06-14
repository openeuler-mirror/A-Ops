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
 * Author: dowzyx
 * Create: 2022-05-23
 * Description: system proc probe
 ******************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <errno.h>
#include <uthash.h>
#include "args.h"

#define METRICS_PROC_NAME   "system_proc"
#define PROC_PATH           "/proc"
#define PROC_COMM           "/proc/%s/comm"
#define PROC_COMM_CMD       "/usr/bin/cat /proc/%s/comm"
#define PROC_STAT           "/proc/%s/stat"
#define PROC_START_TIME_CMD "/usr/bin/cat /proc/%s/stat | awk '{print $22}'"
#define PROC_CMDLINE_CMD    "/proc/%s/cmdline"
#define PROC_FD             "/proc/%s/fd"
#define PROC_FD_CNT_CMD     "/usr/bin/ls -l /proc/%s/fd | wc -l"
#define PROC_IO             "/proc/%s/io"
#define PROC_IO_CMD         "/usr/bin/cat /proc/%s/io"
#define PROC_SMAPS          "/proc/%s/smaps_rollup"
#define PROC_SMAPS_CMD      "/usr/bin/cat /proc/%s/smaps_rollup"
#define PROC_STAT_CMD       "/usr/bin/cat /proc/%s/stat | awk '{print $10\":\"$12\":\"$14\":\"$15\":\"$23\":\"$24}'"
#define PROC_ID_CMD         "ps -eo pid,ppid,pgid,comm | grep -w \"%s\" | awk '{print $2 \"|\" $3}'"
#define PROC_NAME_MAX       64
#define PROC_MAX_RANGE      64
#define LINE_BUF_LEN        128
#define PROC_IN_PROBE_RANGE 1
#define PROBE_TIMES_MAX     200

#define SPLIT_NEWLINE_SYMBOL(s) \
    do { \
        int __len = strlen(s); \
        if (__len > 0 && (s)[__len - 1] == '\n') { \
            (s)[__len - 1] = 0; \
        } \
    } while (0)

enum proc_io_e {
    PROC_IO_RCHAR = 0,
    PROC_IO_WCHAR,
    PROC_IO_SYSCR,
    PROC_IO_SYSCW,
    PROC_IO_READ_BYTES,
    PROC_IO_WRITE_BYTES,
    PROC_IO_CANCEL_WRITE_BYTES,

    PROC_IO_MAX
};

enum proc_stat_e {
    PROC_STAT_MIN_FLT = 0,
    PROC_STAT_MAJ_FLT,
    PROC_STAT_UTIME,
    PROC_STAT_STIME,
    PROC_STAT_VSIZE,
    PROC_STAT_RSS,

    PROC_STAT_MAX
};

enum proc_mss_e {
    PROC_MSS_RESIDENT = 0,
    PROC_MSS_SHARED_CLEAN,
    PROC_MSS_SHARED_DIRTY,
    PROC_MSS_PRIVATE_CLEAN,
    PROC_MSS_PROVATE_DIRTY,
    PROC_MSS_REFERENCED,
    PROC_MSS_ANONYMOUS,
    PROC_MSS_LAZYFREE,
    PROC_MSS_ANONYMOUS_THP,
    PROC_MSS_SWAP,
    PROC_MSS_SHARED_HUGETLB,
    PROC_MSS_PRIVATE_HUGETLB,
    PROC_MSS_PSS,
    PROC_MSS_PSS_LOCKED,
    PROC_MSS_SWAP_PSS,
    PROC_MSS_CHECK_SHNEM_SWAP,

    PROC_MSS_MAX
};

typedef struct {
    unsigned long pid;         // process id
    unsigned long long start_time;  // time the process started
} proc_key_t;

typedef struct {
    char comm[PROC_NAME_MAX];
    int pgid;
    int ppid;
    char *cmdline;
    unsigned int fd_count;              // FROM '/usr/bin/ls -l /proc/[PID]/fd | wc -l'
    unsigned int proc_syscr_count;      // FROM same as 'task_rchar_bytes'
    unsigned int proc_syscw_count;      // FROM same as 'task_rchar_bytes'
    unsigned long long proc_rchar_bytes;    // FROM '/proc/[PID]/io'
    unsigned long long proc_wchar_bytes;    // FROM same as 'task_rchar_bytes'
    unsigned long long proc_read_bytes;     // FROM same as 'task_rchar_bytes'
    unsigned long long proc_write_bytes;    // FROM same as 'task_rchar_bytes'
    unsigned long long proc_cancelled_write_bytes;  // FROM same as 'task_rchar_bytes'
    unsigned int proc_oom_score_adj;    // FROM tracepoint 'oom_score_adj_update'
    unsigned long proc_shared_dirty;    // FROM '/usr/bin/cat /proc/%s/smaps_rollup'
    unsigned long proc_shared_clean;    // FROM same as proc_shared_dirty
    unsigned long proc_private_dirty;   // FROM same as proc_shared_dirty
    unsigned long proc_private_clean;   // FROM same as proc_shared_dirty
    unsigned long proc_referenced;      // FROM same as proc_shared_dirty
    unsigned long proc_lazyfree;        // FROM same as proc_shared_dirty
    unsigned long proc_swap;            // FROM same as proc_shared_dirty
    unsigned long proc_swappss;         // FROM same as proc_shared_dirty
    unsigned long long proc_stat_min_flt;   // FROME '/usr/bin/cat /proc/%s/stat'
    unsigned long long proc_stat_maj_flt;   // FROM same as proc_stat_min_flt
    unsigned long long proc_stat_utime;     // FROM same as proc_stat_min_flt
    unsigned long long proc_stat_stime;     // FROM same as proc_stat_min_flt
    unsigned long long proc_stat_vsize;     // FROM same as proc_stat_min_flt
    unsigned long long proc_stat_rss;       // FROM same as proc_stat_min_flt
} proc_info_t;

typedef struct {
    proc_key_t key;     // key
    char flag;          // whether in proc_range list, 1:yes/0:no
    proc_info_t info;  
    UT_hash_handle hh;
} proc_hash_t;

static int g_probed_times = 0;

static proc_hash_t *g_procmap = NULL;

static char proc_range[PROC_MAX_RANGE][PROC_NAME_MAX] = {
    "go",
    "java",
    "python",
    "python3",
    "dhclient",
    "NetworkManager",
    "dbus",
    "rpcbind",
    "systemd"
};
static int g_proc_range_len = 0;

static void hash_add_proc(proc_hash_t *one_proc)
{
    HASH_ADD(hh, g_procmap, key, sizeof(proc_key_t), one_proc);
    return;
}

static proc_hash_t *hash_find_proc(const char *pid, const char *stime)
{
    proc_hash_t *p = NULL;
    proc_hash_t temp = {0};

    temp.key.pid = (unsigned long)atoi(pid);
    temp.key.start_time = (unsigned long long)atoll(stime);
    HASH_FIND(hh, g_procmap, &temp.key, sizeof(proc_key_t), p);

    return p;
}

static void hash_delete_and_free_proc()
{
    if (g_procmap == NULL) {
        return;
    }
    proc_hash_t *r, *tmp;
    HASH_ITER(hh, g_procmap, r, tmp) {
        HASH_DEL(g_procmap, r);
        if (r != NULL) {
            if (r->info.cmdline != NULL) {
                (void)free(r->info.cmdline);
            }
            (void)free(r);
        }
    }
}

static int is_proc_subdir(const char *pid)
{
    if (*pid >= '1' && *pid <= '9') {
        return 0;
    }
    return -1;
}

static int do_read_line(const char* pid, const char *command, const char *fname, char *buf, unsigned int buf_len)
{
    FILE *f = NULL;
    char fname_or_cmd[LINE_BUF_LEN];
    char line[LINE_BUF_LEN];

    fname_or_cmd[0] = 0;
    (void)snprintf(fname_or_cmd, LINE_BUF_LEN, fname, pid);
    if (access((const char *)fname_or_cmd, 0) != 0) {
        return -1;
    }

    fname_or_cmd[0] = 0;
    line[0] = 0;
    (void)snprintf(fname_or_cmd, LINE_BUF_LEN, command, pid);
    f = popen(fname_or_cmd, "r");
    if (f == NULL) {
        printf("[SYSTEM_PROBE] proc cat fail, popen error.\n");
        return -1;
    }
    if (fgets(line, LINE_BUF_LEN, f) == NULL) {
        (void)pclose(f);
        printf("[SYSTEM_PROBE] proc get_info fail, line is null.\n");
        return -1;
    }
    
    SPLIT_NEWLINE_SYMBOL(line);
    (void)strncpy(buf, line, buf_len - 1);
    (void)pclose(f);
    return 0;
}

static int get_proc_comm(const char* pid, char *buf)
{
    return do_read_line(pid, PROC_COMM_CMD, PROC_COMM, buf, PROC_NAME_MAX);
}

static int get_proc_start_time(const char* pid, char *buf)
{
    return do_read_line(pid, PROC_START_TIME_CMD, PROC_STAT, buf, PROC_NAME_MAX);
}

static void get_proc_id(proc_info_t *proc_info)
{
    FILE *f = NULL;
    char cmd[LINE_BUF_LEN];
    char line[LINE_BUF_LEN];

    if (strlen(proc_info->comm) == 0) {
        /* comm is NULL, return */
        return;
    }

    cmd[0] = 0;
    (void)snprintf(cmd, LINE_BUF_LEN, PROC_ID_CMD, proc_info->comm);
    f = popen(cmd, "r");
    if (f == NULL) {
        goto out;
    }
    while (!feof(f)) {
        line[0] = 0;
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            goto out;
        }
        SPLIT_NEWLINE_SYMBOL(line);

        (void)sscanf(line, "%d %*c %d", &proc_info->ppid, &proc_info->pgid);
    }

out:
    if (f != NULL) {
        pclose(f);
    }
    return;
}

#define JINFO_NOT_INSTALLED 0
#define JINFO_IS_INSTALLED  1

static int is_jinfo_installed()
{
    FILE *f = NULL;
    char cmd[LINE_BUF_LEN];
    char line[LINE_BUF_LEN];
    int is_installed = JINFO_NOT_INSTALLED;

    cmd[0] = 0;
    (void)snprintf(cmd, LINE_BUF_LEN, "which jinfo");
    f = popen(cmd, "r");
    if (f == NULL) {
        goto out;
    }
    if (fgets(line, LINE_BUF_LEN, f) == NULL) {
        goto out;
    }
    if (strstr(line, "no jinfo in") == NULL) {
        is_installed = JINFO_IS_INSTALLED;
    }
out:
    if (f != NULL) {
        (void)pclose(f);
    }
    return is_installed;
}

#define TASK_PROBE_JAVA_COMMAND "sun.java.command"
static void get_java_proc_cmd(const char* pid, proc_info_t *proc_info)
{
    FILE *f = NULL;
    char cmd[LINE_BUF_LEN];
    char line[LINE_BUF_LEN];
    if (is_jinfo_installed() == JINFO_NOT_INSTALLED) {
        printf("[SYSTEM_PROBE] jinfo not installed, please check.\n");
        return;
    }
    cmd[0] = 0;
    (void)snprintf(cmd, LINE_BUF_LEN, "jinfo %s | grep %s | awk '{print $3}'", pid, TASK_PROBE_JAVA_COMMAND);
    f = popen(cmd, "r");
    if (f == NULL) {
        goto out;
    }
    if (fgets(line, LINE_BUF_LEN, f) == NULL) {
        goto out;
    }
    SPLIT_NEWLINE_SYMBOL(line);
    proc_info->cmdline = (char *)malloc(LINE_BUF_LEN);
    (void)memset(proc_info->cmdline, 0, LINE_BUF_LEN);
    (void)strncpy(proc_info->cmdline, line, LINE_BUF_LEN - 1);
out:
    if (f != NULL) {
        (void)pclose(f);
    }
    return;
}

static int get_proc_cmdline(const char* pid, proc_info_t *proc_info)
{
    FILE *f = NULL;
    char path[LINE_BUF_LEN];
    char line[LINE_BUF_LEN];
    int index = 0;

    path[0] = 0;
    line[0] = 0;
    (void)snprintf(path, LINE_BUF_LEN, PROC_CMDLINE_CMD, pid);
    f = fopen(path, "r");
    if (f == NULL) {
        return -1;
    }
    /* parse line */
    while (!feof(f)) {
        if (index >= LINE_BUF_LEN - 1) {
            line[index] = '\0';
            break;
        }
        line[index] = fgetc(f);
        if (line[index] == '\0') {
            line[index] = ' ';
        } else if (line[index] == -1 && line[index - 1] == ' ') {
            line[index - 1] = '\0';
        }
        index++;
    }
    if (index <= 1) {
        goto out;
    }
    proc_info->cmdline = (char *)malloc(LINE_BUF_LEN);
    (void)memset(proc_info->cmdline, 0, LINE_BUF_LEN);
    (void)strncpy(proc_info->cmdline, line, LINE_BUF_LEN - 1);
out:
    (void)fclose(f);
    return 0;
}

static int get_proc_fdcnt(const char *pid, proc_info_t *proc_info)
{
    char buffer[LINE_BUF_LEN];
    buffer[0] = 0;
    int ret = do_read_line(pid, PROC_FD_CNT_CMD, PROC_FD, buffer, LINE_BUF_LEN);
    if (ret < 0) {
        return -1;
    }
    proc_info->fd_count = (unsigned int)atoi(buffer);
    return 0;
}

static void do_set_proc_stat(proc_info_t *proc_info, char *buf, int index)
{
    unsigned long long value = (unsigned long long)atoll(buf);
    switch (index)
    {
        case PROC_STAT_MIN_FLT:
            proc_info->proc_stat_min_flt = value;
            break;
        case PROC_STAT_MAJ_FLT:
            proc_info->proc_stat_maj_flt = value;
            break;
        case PROC_STAT_UTIME:
            proc_info->proc_stat_utime = value;
            break;
        case PROC_STAT_STIME:
            proc_info->proc_stat_stime = value;
            break;
        case PROC_STAT_VSIZE:
            proc_info->proc_stat_vsize = value;
            break;
        case PROC_STAT_RSS:
            proc_info->proc_stat_rss = value;
            break;
        default:
            break;
    }
}

static int get_proc_stat(const char *pid, proc_info_t *proc_info)
{
    char buffer[LINE_BUF_LEN];
    char *p = NULL;
    int index = 0;
    buffer[0] = 0;
    int ret = do_read_line(pid, PROC_STAT_CMD, PROC_STAT, buffer, LINE_BUF_LEN);

    if (ret < 0) {
        return -1;
    }
    p = strtok(buffer, ":");
    while (p != NULL && index < PROC_STAT_MAX) {
        do_set_proc_stat(proc_info, p, index);
        p = strtok(NULL, ":");
        index++;
    }

    return 0;
}

static void do_set_proc_io(proc_info_t *proc_info, unsigned long long value, int index)
{
    switch (index)
    {
        case PROC_IO_RCHAR:
            proc_info->proc_rchar_bytes = value;
            break;
        case PROC_IO_WCHAR:
            proc_info->proc_wchar_bytes = value;
            break;
        case PROC_IO_SYSCR:
            proc_info->proc_syscr_count = value;
            break;
        case PROC_IO_SYSCW:
            proc_info->proc_syscw_count = value;
            break;
        case PROC_IO_READ_BYTES:
            proc_info->proc_read_bytes = value;
            break;
        case PROC_IO_WRITE_BYTES:
            proc_info->proc_write_bytes = value;
            break;
        case PROC_IO_CANCEL_WRITE_BYTES:
            proc_info->proc_cancelled_write_bytes = value;
            break;
        default:
            break;
    }
}

int get_proc_io(const char *pid, proc_info_t *proc_info)
{
    FILE *f = NULL;
    int index = 0;
    unsigned long long value = 0;
    char fname_or_cmd[LINE_BUF_LEN];
    char line[LINE_BUF_LEN];

    fname_or_cmd[0] = 0;
    (void)snprintf(fname_or_cmd, LINE_BUF_LEN, PROC_IO, pid);
    if (access((const char *)fname_or_cmd, 0) != 0) {
        goto out;
    }
    fname_or_cmd[0] = 0;
    (void)snprintf(fname_or_cmd, LINE_BUF_LEN, PROC_IO_CMD, pid);
    f = popen(fname_or_cmd, "r");
    if (f == NULL) {
        goto out;
    }
    while (!feof(f) && (index < PROC_IO_MAX)) {
        line[0] = 0;
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            goto out;
        }
        value = 0;
        if (sscanf(line, "%*s %llu", &value) < 1) {
            goto out;
        }
        do_set_proc_io(proc_info, value, index);
        index++;
    }
out:
    if (f != NULL) {
        (void)pclose(f);
    }
    return 0;
}

static void do_set_proc_mss(proc_info_t *proc_info, unsigned long value, int index)
{
    switch (index)
    {
        case PROC_MSS_SHARED_CLEAN:
            proc_info->proc_shared_clean = value;
            break;
        case PROC_MSS_SHARED_DIRTY:
            proc_info->proc_shared_dirty = value;
            break;
        case PROC_MSS_PRIVATE_CLEAN:
            proc_info->proc_private_clean = value;
            break;
        case PROC_MSS_PROVATE_DIRTY:
            proc_info->proc_private_dirty = value;
            break;
        case PROC_MSS_REFERENCED:
            proc_info->proc_referenced = value;
            break;
        case PROC_MSS_LAZYFREE:
            proc_info->proc_lazyfree = value;
            break;
        case PROC_MSS_SWAP:
            proc_info->proc_swap = value;
            break;
        case PROC_MSS_SWAP_PSS:
            proc_info->proc_swappss = value;
            break;
        default:
            break;
    }
}

int get_proc_mss(const char *pid, proc_info_t *proc_info)
{
    FILE *f = NULL;
    int index = 0;
    unsigned long value = 0;
    char fname_or_cmd[LINE_BUF_LEN];
    char line[LINE_BUF_LEN];

    fname_or_cmd[0] = 0;
    (void)snprintf(fname_or_cmd, LINE_BUF_LEN, PROC_SMAPS, pid);
    if (access((const char *)fname_or_cmd, 0) != 0) {
        goto out;
    }
    fname_or_cmd[0] = 0;
    (void)snprintf(fname_or_cmd, LINE_BUF_LEN, PROC_SMAPS_CMD, pid);
    f = popen(fname_or_cmd, "r");
    if (f == NULL) {
        goto out;
    }
    while (!feof(f) && (index < PROC_MSS_MAX)) {
        line[0] = 0;
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            goto out;
        }
        value = 0;
        if (sscanf(line, "%*s %lu %*s", &value) < 0) {
            goto out;
        }
        do_set_proc_mss(proc_info, value, index);
        index++;
    }
out:
    if (f != NULL) {
        (void)pclose(f);
    }
    return 0;
}

static int update_proc_infos(const char *pid, proc_info_t *proc_info)
{
    int ret = 0;

    (void)get_proc_id(proc_info);

    ret = get_proc_fdcnt(pid, proc_info);
    if (ret < 0) {
        return -1;
    }
    // TODO: other infos
    ret = get_proc_io(pid, proc_info);
    if (ret < 0) {
        return -1;
    }

    ret = get_proc_mss(pid, proc_info);
    if (ret < 0) {
        return -1;
    }

    ret = get_proc_stat(pid, proc_info);
    if (ret < 0) {
        return -1;
    }

    return 0;
}

static int check_proc_probe_flag(const char *comm)
{
    int index;
    for (index = 0; index < g_proc_range_len; index++) {
        if (strcmp(comm, proc_range[index]) == 0) {
            return 1;
        }
    }
    return 0;
}

static void output_proc_infos(proc_hash_t *one_proc)
{
    fprintf(stdout,
        "|%s|%lu|%d|%d|%s|%s|%u|%llu|%llu|%u|%u|%llu|%llu|%llu|%lu|%lu|%lu|%lu|%lu|%lu|%lu|%lu|%llu|%llu|%llu|%llu|%llu|%llu|\n",
        METRICS_PROC_NAME,
        one_proc->key.pid,
        one_proc->info.pgid,
        one_proc->info.ppid,
        one_proc->info.comm,
        one_proc->info.cmdline == NULL ? "" : one_proc->info.cmdline,
        one_proc->info.fd_count,
        one_proc->info.proc_rchar_bytes,
        one_proc->info.proc_wchar_bytes,
        one_proc->info.proc_syscr_count,
        one_proc->info.proc_syscw_count,
        one_proc->info.proc_read_bytes,
        one_proc->info.proc_write_bytes,
        one_proc->info.proc_cancelled_write_bytes,
        one_proc->info.proc_shared_clean,
        one_proc->info.proc_shared_dirty,
        one_proc->info.proc_private_clean,
        one_proc->info.proc_private_dirty,
        one_proc->info.proc_referenced,
        one_proc->info.proc_lazyfree,
        one_proc->info.proc_swap,
        one_proc->info.proc_swappss,
        one_proc->info.proc_stat_min_flt,
        one_proc->info.proc_stat_maj_flt,
        one_proc->info.proc_stat_utime,
        one_proc->info.proc_stat_stime,
        one_proc->info.proc_stat_vsize,
        one_proc->info.proc_stat_rss);
    return;
}

int system_proc_probe()
{
    int ret = 0;
    DIR *dir = NULL;
    struct dirent *entry;
    char comm[PROC_NAME_MAX];
    char stime[PROC_NAME_MAX];
    proc_hash_t *l, *p = NULL;

    // check timeout
    if (g_probed_times >= PROBE_TIMES_MAX) {
        hash_delete_and_free_proc();
    }

    dir = opendir(PROC_PATH);
    if (dir == NULL) {
        return -1;
    }
    while (entry = readdir(dir)) {
        if (is_proc_subdir(entry->d_name) == -1) {
            continue;
        }
        /* proc start time(avoid repetition of pid) */
        (void)memset(stime, 0, PROC_NAME_MAX);
        (void)get_proc_start_time(entry->d_name, stime);

        /* if the proc(pid+start_time) is finded in g_procmap, it means
           the proc was probed before and output proc_infos directly */
        p = hash_find_proc(entry->d_name, stime);
        if (p != NULL && p->flag == PROC_IN_PROBE_RANGE) {
            (void)update_proc_infos(entry->d_name, &p->info);
            output_proc_infos(p);
            continue;
        }

        (void)memset(comm, 0, PROC_NAME_MAX);
        (void)get_proc_comm(entry->d_name, comm);

        /* check proc whether in proc_range, if in this proc should be probed */
        if (check_proc_probe_flag(comm) != PROC_IN_PROBE_RANGE) {
            continue;
        } else {
            l = (proc_hash_t *)malloc(sizeof *l);
            (void)memset(l, 0, sizeof *l);
            l->key.pid = (unsigned long)atoi(entry->d_name);
            l->key.start_time = (unsigned long long)atoll(stime);
            (void)strncpy(l->info.comm, comm, PROC_NAME_MAX - 1);
            l->flag = PROC_IN_PROBE_RANGE;
            if (strcmp(comm, "java") == 0) {
                (void)get_java_proc_cmd(entry->d_name, &l->info);
            } else {
                (void)get_proc_cmdline(entry->d_name, &l->info);
            }
        }

        (void)update_proc_infos(entry->d_name, &l->info);

        /* add new_proc to hashmap and output */
        hash_add_proc(l);
        output_proc_infos(l);
    }
    closedir(dir);
    g_probed_times++;
    return 0;
}

void system_proc_init(char *task_whitelist)
{
    FILE *f = NULL;
    char line[PROC_NAME_MAX];
    
    for (int i = 0; i < PROC_MAX_RANGE; i++) {
        if (strlen(proc_range[i]) == 0) {
            g_proc_range_len = i;       // init proc_range's length
            break;
        }
    }

    if (task_whitelist == NULL || strlen(task_whitelist) == 0) {
        return;
    }

    f = fopen(task_whitelist, "r");
    if (f == NULL) {
        return;
    }
    while (!feof(f)) {
        (void)memset(line, 0, PROC_NAME_MAX);
        if (fgets(line, PROC_NAME_MAX, f) == NULL) {
            goto out;
        }
        SPLIT_NEWLINE_SYMBOL(line);
        if (strlen(line) == 0) {
            continue;
        }
        /* update procname to proc_range list */
        (void)strncpy(proc_range[g_proc_range_len], line, PROC_NAME_MAX - 1);
        g_proc_range_len++;
    }
out:
    fclose(f);
    return;
}
