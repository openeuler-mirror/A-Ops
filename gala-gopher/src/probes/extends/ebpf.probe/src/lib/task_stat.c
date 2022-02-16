/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
 */
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <unistd.h>

#include "bpf.h"

#define PROC_TASK_FILE "/proc/%u/stat"
#define AWK_FIELD "\"\%u=\"$\%u\"\\n\""
#define AWK_FIELD2 "\"\%u=\"$\%u"
#define AWK_COMMAND_BEGIN " | awk '{print"
#define AWK_COMMAND_END   "}'"
#define CAT_COMMAND   "/usr/bin/cat %s %s"
#define DEL_SYMBOL "="
#define PROC_CWD_FILE "/proc/%d/cwd"
#define PROC_EXE_FILE "/proc/%d/exe"

enum task_stat_e {
    TASK_STAT_MINFLT = 10,
    TASK_STAT_MAJFLT = 12,
    TASK_STAT_UTIME = 14,
    TASK_STAT_STIME = 15,
    TASK_STAT_VSIZE = 23,
    TASK_STAT_RSS   = 24,
    TASK_STAT_MAX   = TASK_STAT_RSS + 1
};

#define UN_USED 0
#define IN_USED 1
struct task_stat_s {
    int used;
    long long stat[TASK_STAT_MAX];
};

#define MAX_NUM 10
static unsigned int task_stat_index = 0;
static struct task_stat_s stats[MAX_NUM] = {{0}};
static char awk_command[COMMAND_LEN] = {0};

int __get_next_index()
{
    int num = 0;
    task_stat_index = task_stat_index % MAX_NUM;

    while (stats[task_stat_index].used == IN_USED) {
        task_stat_index++;
        num++;
        task_stat_index = task_stat_index % MAX_NUM;
        if (num >= MAX_NUM) {
            return -1;
        }
    }

    stats[task_stat_index].used = IN_USED;
    return task_stat_index;
}

void __free_index(unsigned int i_index)
{
    i_index = i_index % MAX_NUM;
    stats[i_index].used = UN_USED;
}

char* __get_awk_command()
{   
    int len;

    if (awk_command[0] != 0) {
        return awk_command;
    }

    len = snprintf(awk_command, COMMAND_LEN, "%s", AWK_COMMAND_BEGIN);
    if (len < 0) {
        return NULL;
    }
    
    len += snprintf(awk_command + len, COMMAND_LEN - len, AWK_FIELD, TASK_STAT_MINFLT, TASK_STAT_MINFLT);
    if (len < 0) {
        return NULL;
    }
    len += snprintf(awk_command + len, COMMAND_LEN - len, AWK_FIELD, TASK_STAT_MAJFLT, TASK_STAT_MAJFLT);
    if (len < 0) {
        return NULL;
    }
    len += snprintf(awk_command + len, COMMAND_LEN - len, AWK_FIELD, TASK_STAT_UTIME, TASK_STAT_UTIME);
    if (len < 0) {
        return NULL;
    }
    len += snprintf(awk_command + len, COMMAND_LEN - len, AWK_FIELD, TASK_STAT_STIME, TASK_STAT_STIME);
    if (len < 0) {
        return NULL;
    }
    len += snprintf(awk_command + len, COMMAND_LEN - len, AWK_FIELD, TASK_STAT_VSIZE, TASK_STAT_VSIZE);
    if (len < 0) {
        return NULL;
    }
    len += snprintf(awk_command + len, COMMAND_LEN - len, AWK_FIELD2, TASK_STAT_RSS, TASK_STAT_RSS);
    if (len < 0) {
        return NULL;
    }
    len += snprintf(awk_command + len, COMMAND_LEN - len, "%s", AWK_COMMAND_END);
    if (len < 0) {
        return NULL;
    }
    return awk_command;
}

int __build_cat_command(char *stat_file, char cat_command[], unsigned int buf_len)
{
    char *awk;

    awk = __get_awk_command();
    if (awk == NULL) {
        return -1;
    }

    (void)snprintf(cat_command, buf_len, CAT_COMMAND, stat_file, awk);
    return 0;
}

void __get_line_info(char *line, unsigned int *stat_index, long long *value)
{
    char *s1, *s2;
    s1 = strtok(line, DEL_SYMBOL);
    s2 = strtok(NULL, DEL_SYMBOL);

    *stat_index = (unsigned int)atoi(s1);
    *value = (long long)atol(s2);
}

int read_task_stat(unsigned int pid)
{
    FILE *f = NULL;
    int i = -1;
    unsigned int stat_index;
    long long value;
    char stat_file[COMMAND_LEN];
    char cat_command[COMMAND_LEN];
    char line[LINE_BUF_LEN];

    stat_file[0] = 0;
    (void)snprintf(stat_file, COMMAND_LEN, PROC_TASK_FILE, pid);
    
    if (access((const char *)stat_file, 0) != 0) {
        printf("No such file or directory: %s\r\n", stat_file);
        goto out;
    }

    cat_command[0] = 0;
    if (__build_cat_command(stat_file, cat_command, COMMAND_LEN) < 0) {
        goto out;
    }

    f = popen(cat_command, "r");
    if (f == NULL) {
        goto out;
    }

    i = __get_next_index();
    if (i < 0) {
        goto out;
    }

    while (!feof(f)) {
        line[0] = 0;
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            goto out;
        }
        SPLIT_NEWLINE_SYMBOL(line);
        __get_line_info(line, &stat_index, &value);

        if (stat_index < TASK_STAT_MAX) {
            stats[i].stat[stat_index] = value;
        }
    }

out:
    if (f != NULL) {
        (void)pclose(f);
    }
    
    return i;
}

void free_task_stat(unsigned int read_handle)
{
    __free_index(read_handle);
}

long long get_task_minflt(unsigned int read_handle)
{
    if (read_handle < MAX_NUM) {
        return stats[read_handle].stat[TASK_STAT_MINFLT];
    }
    return 0;
}

long long get_task_majflt(unsigned int read_handle)
{
    if (read_handle < MAX_NUM) {
        return stats[read_handle].stat[TASK_STAT_MAJFLT];
    }
    return 0;
}

long long get_task_utime(unsigned int read_handle)
{
    if (read_handle < MAX_NUM) {
        return stats[read_handle].stat[TASK_STAT_UTIME];
    }
    return 0;
}

long long get_task_stime(unsigned int read_handle)
{
    if (read_handle < MAX_NUM) {
        return stats[read_handle].stat[TASK_STAT_STIME];
    }
    return 0;
}

long long get_task_vsize(unsigned int read_handle)
{
    if (read_handle < MAX_NUM) {
        return stats[read_handle].stat[TASK_STAT_VSIZE];
    }
    return 0;
}

long long get_task_rss(unsigned int read_handle)
{
    if (read_handle < MAX_NUM) {
        return stats[read_handle].stat[TASK_STAT_RSS];
    }
    return 0;
}

int get_task_pwd(int pid, char *pwd)
{
    int ret;
    char pwd_file[COMMAND_LEN] = {0};
    char *buf = pwd;

    if (pid < 0) {
        return -1;
    }
    (void)snprintf(pwd_file, COMMAND_LEN, PROC_CWD_FILE, pid);
    ret = readlink(pwd_file, buf, COMMAND_LEN);
    if (ret < 0) {
        perror("readlink ");
        return -1;
    }
    buf[ret] = '\0';
	return 0;
}

int get_task_exe(int pid, char *exe, int exe_len)
{
    int ret;
    char pwd_file[COMMAND_LEN] = {0};
    char *buf = exe;
    int buf_len = (exe_len <= COMMAND_LEN) ? exe_len : COMMAND_LEN;

    if (pid < 0) {
        return -1;
    }
    (void)snprintf(pwd_file, COMMAND_LEN, PROC_EXE_FILE, pid);
    ret = readlink(pwd_file, buf, buf_len - 1);
    if (ret < 0) {
        perror("readlink ");
        return -1;
    }
    buf[ret] = '\0';
	return 0;
}
