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
 * Author: luzhihao
 * Create: 2022-02-25
 * Description: task io statistic
 ******************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <unistd.h>

#include "bpf.h"
#include "task.h"

#define TASK_IO "/proc/%d/io"
#define TASK_IO_COMMAND "/usr/bin/cat /proc/%d/io"

enum task_io_e {
    TASK_IO_RCHAR = 0,
    TASK_IO_WCHAR,
    TASK_IO_SYSCR,
    TASK_IO_SYSCW,
    TASK_IO_READ_BYTES,
    TASK_IO_WRITE_BYTES,
    TASK_IO_CANCEL_WRITE_BYTES,

    TASK_IO_MAX
};

static void __do_set_task_io(struct process_io_data *io_data, __u64 value, int index)
{
    switch (index)
    {
        case TASK_IO_RCHAR:
            io_data->task_rchar_bytes = value;
            break;
        case TASK_IO_WCHAR:
            io_data->task_wchar_bytes = value;
            break;
        case TASK_IO_SYSCR:
            io_data->task_syscr_count = value;
            break;
        case TASK_IO_SYSCW:
            io_data->task_syscw_count = value;
            break;
        case TASK_IO_READ_BYTES:
            io_data->task_read_bytes = value;
            break;
        case TASK_IO_WRITE_BYTES:
            io_data->task_write_bytes = value;
            break;
        case TASK_IO_CANCEL_WRITE_BYTES:
            io_data->task_cancelled_write_bytes = value;
            break;
        default:
            break;
    }
}

static void __do_get_task_io(char *line, __u64 *value)
{
    char *s1, *s2;
    s1 = strtok(line, ":");
    s2 = strtok(NULL, ":");

    (void)s1;
    SPLIT_NEWLINE_SYMBOL(s2);
    *value = (__u64)atoll((const char *)s2);
}

int get_task_io(struct process_io_data *io_data, int pid)
{
    FILE *f = NULL;
    int index;
    __u64 value;
    char file_or_command[COMMAND_LEN];
    char line[LINE_BUF_LEN];

    file_or_command[0] = 0;
    (void)snprintf(file_or_command, COMMAND_LEN, TASK_IO, pid);
    if (access((const char *)file_or_command, 0) != 0) {
        goto out;
    }

    file_or_command[0] = 0;
    (void)snprintf(file_or_command, COMMAND_LEN, TASK_IO_COMMAND, pid);

    f = popen(file_or_command, "r");
    if (f == NULL) {
        goto out;
    }

    index = 0;
    while (!feof(f) && (index < TASK_IO_MAX)) {
        line[0] = 0;
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            goto out;
        }

        __do_get_task_io(line, &value);
        __do_set_task_io(io_data, value, index);
        index++;
    }

out:
    if (f != NULL) {
        (void)pclose(f);
    }

    return 0;
}
