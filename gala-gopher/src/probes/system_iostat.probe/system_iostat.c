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
 * Author: dowzyx
 * Create: 2022-03-10
 * Description: system iostat probe
 ******************************************************************************/
#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include "args.h"

/*
[root@localhost ~]# iostat -xd -t 5
Device r/s rkB/s rrqm/s %rrqm r_await rareq-sz w/s wkB/s wrqm/s %wrqm w_await wareq-sz d/s dkB/s drqm/s %drqm d_await dareq-sz aqu-sz %util
 sda  0.28 19.59  0.00  0.00   0.58    68.93  1.69 65.02  0.00   0.00  0.81    38.57  0.00  0.00  0.00  0.00   0.00     0.00    0.00  0.09
*/

#define METRICS_NAME        "system_iostat"
#define SYSTEM_DISKSTATS_COMMAND \
    "iostat -xd | awk 'NR>1 {print $1\":\"$2\":\"$3\":\"$6\":\"$7\":\"$8\":\"$9\":\"$11\":\"$12\":\"$21}'"
#define IOSTAT_IS_EXIST     "which iostat"
#define DISK_DEV_NAME_SIZE  32
#define LINE_BUF_LEN        256
#define DATA_LEN            64

#define METRICS_IOSTAT_DEVNAME      0
#define METRICS_IOSTAT_RD_SPEED     1
#define METRICS_IOSTAT_RDKB_SPEED   2
#define METRICS_IOSTAT_RD_AWAIT     3
#define METRICS_IOSTAT_RAREQ_SZ     4
#define METRICS_IOSTAT_WR_SPEED     5
#define METRICS_IOSTAT_WRKB_SPEED   6
#define METRICS_IOSTAT_WR_AWAIT     7
#define METRICS_IOSTAT_WAREQ_SZ     8
#define METRICS_IOSTAT_UTIL         9
#define METRICS_IOSTAT_MAX          10

#define SPLIT_NEWLINE_SYMBOL(s) \
    do { \
        int __len = strlen(s); \
        if (__len > 0 && (s)[__len - 1] == '\n') { \
            (s)[__len - 1] = 0; \
        } \
    } while (0)

int main(struct probe_params * params)
{
    int ret;
    FILE* f = NULL;
    char line[LINE_BUF_LEN];
    char cmd[LINE_BUF_LEN];
    char *p;
    int index;
    char iostat_buf[METRICS_IOSTAT_MAX][DATA_LEN];

    /* check whether iostat is installed in this OS */
    cmd[0] = 0;
    (void)snprintf(cmd, LINE_BUF_LEN, IOSTAT_IS_EXIST);
    f = popen(cmd, "r");
    if (f ==NULL) {
        printf("[SYSTEM_IOSTAT] iostat not exist, please install sysstat.\n");
        return -1;
    }
    (void)pclose(f);

    /* obtain IO statistics */
    (void)memset(cmd, 0, LINE_BUF_LEN);
    (void)snprintf(cmd, LINE_BUF_LEN, SYSTEM_DISKSTATS_COMMAND);
    f = popen(cmd, "r");
    if (f ==NULL) {
        printf("[SYSTEM_IOSTAT] iostat fail, popen error.\n");
        return -1;
    }
    while (!feof(f)) {
        (void)memset(line, 0, LINE_BUF_LEN);
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            pclose(f);
            return -1;
        }
        if (strstr(line, "Device") != NULL ||
            strstr(line, "::") != NULL) {
            continue;
        }
        SPLIT_NEWLINE_SYMBOL(line);

        p = strtok(line, ":");
        index = 0;
        while (p != NULL && index < METRICS_IOSTAT_MAX) {
            memset(iostat_buf[index], 0, DATA_LEN);
            strcpy(iostat_buf[index], p);
            p = strtok(NULL, ":");
            index++;
        }
        /* output */
        fprintf(stdout,
            "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n",
            METRICS_NAME,
            iostat_buf[METRICS_IOSTAT_DEVNAME],
            iostat_buf[METRICS_IOSTAT_RD_SPEED],
            iostat_buf[METRICS_IOSTAT_RDKB_SPEED],
            iostat_buf[METRICS_IOSTAT_RD_AWAIT],
            iostat_buf[METRICS_IOSTAT_RAREQ_SZ],
            iostat_buf[METRICS_IOSTAT_WR_SPEED],
            iostat_buf[METRICS_IOSTAT_WRKB_SPEED],
            iostat_buf[METRICS_IOSTAT_WR_AWAIT],
            iostat_buf[METRICS_IOSTAT_WAREQ_SZ],
            iostat_buf[METRICS_IOSTAT_UTIL]);
    }

    (void)pclose(f);
    return 0;
}
