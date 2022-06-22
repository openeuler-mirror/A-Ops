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
 * Create: 2022-03-01
 * Description: system disk probe
 ******************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "common.h"
#include "event.h"
#include "system_disk.h"

#define METRICS_DISK_NAME       "system_disk"
#define METRICS_IOSTAT_NAME     "system_iostat"
#define SYSTEM_INODE_COMMAND \
    "/usr/bin/df -i | /usr/bin/awk 'NR>1 {print $1\"%\"$2\"%\"$3\"%\"$4\"%\"$5\"%\"$6}'"
#define SYSTEM_BLOCK_CMD \
    "/usr/bin/df | /usr/bin/awk '{if($6==\"%s\"){print $1\"%\"$2\"%\"$3\"%\"$4\"%\"$5\"%\"$6}}'"
#define IOSTAT_IS_EXIST         "which iostat"
#define SYSTEM_DISKSTATS_COMMAND \
    "iostat -xd | /usr/bin/awk 'NR>1 {print $1\":\"$2\":\"$3\":\"$6\":\"$7\":\"$8\":\"$9\":\"$11\":\"$12\":\"$21}'"

#define METRICS_DF_FSYS_TYPE        0
#define METRICS_DF_INODES_OR_BLOCKS 1
#define METRICS_DF_USED             2
#define METRICS_DF_FREE             3
#define METRICS_DF_USE_PER          4
#define METRICS_DF_MOUNTED          5
#define METRICS_DF_FIELD_MAX        6

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

static void split_line_to_substrings(char *line, char *pp[], int max_pp_len)
{
    char *str = line;
    char *ptoken = NULL;
    char *psave = NULL;
    int index = 0;

    ptoken = strtok_r(str, "%", &psave);
    while (ptoken != NULL && index < max_pp_len) {
        pp[index++] = ptoken;
        ptoken = strtok_r(NULL, "%", &psave);
    }

    return;
}

static void report_disk_status(char *inode_info[], char *block_info[], struct probe_params *params)
{
    char entityid[LINE_BUF_LEN];
    int inode_used_per;
    int block_used_per;

    if (params->logs == 0) {
        return;
    }

    entityid[0] = 0;
    inode_used_per = atoi(inode_info[METRICS_DF_USE_PER]);
    block_used_per = atoi(block_info[METRICS_DF_USE_PER]);

    if (inode_used_per > params->res_percent_upper) {
        (void)strncpy(entityid, inode_info[METRICS_DF_MOUNTED], LINE_BUF_LEN - 1);
        report_logs(METRICS_DISK_NAME,
                    entityid,
                    "inode_userd_per",
                    EVT_SEC_WARN,
                    "Too many Inodes consumed(%d).",
                    inode_used_per);
    }
    if (block_used_per > params->res_percent_upper) {
        if (entityid[0] == 0) {
            (void)strncpy(entityid, inode_info[METRICS_DF_MOUNTED], LINE_BUF_LEN - 1);
        }
        report_logs(METRICS_DISK_NAME,
                    entityid,
                    "block_userd_per",
                    EVT_SEC_WARN,
                    "Too many Blocks used(%d).",
                    block_used_per);
    }
}

static int get_mnt_block_info(const char *mounted_on, char *block_info[])
{
    FILE *f = NULL;
    char cmd[LINE_BUF_LEN];
    char line[LINE_BUF_LEN];

    cmd[0] = 0;
    (void)snprintf(cmd, LINE_BUF_LEN, SYSTEM_BLOCK_CMD, mounted_on);
    f = popen(cmd, "r");
    if (f == NULL) {
        return -1;
    }
    line[0] = 0;
    if (fgets(line, LINE_BUF_LEN, f) == NULL) {
        pclose(f);
        return -1;
    }
    SPLIT_NEWLINE_SYMBOL(line);
    split_line_to_substrings(line, block_info, METRICS_DF_FIELD_MAX);

    pclose(f);
    return 0;
}

/*
 [root@localhost ~]# df -i | awk 'NR>1 {print $1"%"$2"%"$3"%"$4"%"$5"%"$6}'
 devtmpfs%949375%377%948998%1%%/dev
 tmpfs%952869%1%952868%1%%/dev/shm
 tmpfs%952869%631%952238%1%%/run
 [root@localhost ~]# df | awk '{if($6==/dev){print $1"%"$2"%"$3"%"$4"%"$5"%"$6}}'
 devtmpfs%3797500%0%3797500%0%%/dev
 */
int system_disk_probe(struct probe_params *params)
{
    FILE *f = NULL;
    char line[LINE_BUF_LEN];
    char *inode_info[METRICS_DF_FIELD_MAX];
    char *block_info[METRICS_DF_FIELD_MAX];

    /* get every disk filesystem's inode infos */
    f = popen(SYSTEM_INODE_COMMAND, "r");
    if (f == NULL) {
        return -1;
    }
    while (!feof(f)) {
        line[0] = 0;
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            break;
        }
        SPLIT_NEWLINE_SYMBOL(line);
        split_line_to_substrings(line, inode_info, METRICS_DF_FIELD_MAX);

        if (get_mnt_block_info(inode_info[METRICS_DF_MOUNTED], block_info) < 0) {
            break;
        }
        /* output */
        (void)fprintf(stdout, "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n",
            METRICS_DISK_NAME,
            inode_info[METRICS_DF_MOUNTED],
            inode_info[METRICS_DF_FSYS_TYPE],
            inode_info[METRICS_DF_INODES_OR_BLOCKS],
            inode_info[METRICS_DF_USE_PER],
            inode_info[METRICS_DF_USED],
            inode_info[METRICS_DF_FREE],
            block_info[METRICS_DF_INODES_OR_BLOCKS],
            block_info[METRICS_DF_USE_PER],
            block_info[METRICS_DF_USED],
            block_info[METRICS_DF_FREE]);
        /* output event */
        report_disk_status(inode_info, block_info, params);
    }
    (void)pclose(f);
    return 0;
}

static void report_disk_iostat(char *iostat[], struct probe_params *params)
{
    char entityid[LINE_BUF_LEN];

    if (params->logs == 0) {
        return;
    }

    entityid[0] = 0;

    if (atof(iostat[METRICS_IOSTAT_UTIL]) > params->res_percent_upper) {
        (void)strncpy(entityid, iostat[METRICS_IOSTAT_DEVNAME], LINE_BUF_LEN - 1);
        report_logs(METRICS_IOSTAT_NAME,
                    entityid,
                    "iostat_util",
                    EVT_SEC_WARN,
                    "Disk device saturated(%s).",
                    iostat[METRICS_IOSTAT_UTIL]);
    }
}

/*
 [root@localhost ~]# iostat -xd -t 5
 Device r/s rkB/s r_await rareq-sz w/s wkB/s w_await wareq-sz d/s  dkB/s drqm/s %drqm d_await dareq-sz aqu-sz %util
  sda  0.28 19.59  0.58    68.93  1.69 65.02  0.81    38.57  0.00  0.00  0.00   0.00   0.00     0.00    0.00  0.09
 */
int system_iostat_probe(struct probe_params *params)
{
    FILE* f = NULL;
    char line[LINE_BUF_LEN];
    int index;
    char *ptoken;
    char *psave;
    char *pp[METRICS_IOSTAT_MAX];

    /* check whether iostat is installed in this OS */
    f = popen(IOSTAT_IS_EXIST, "r");
    if (f == NULL) {
        printf("[SYSTEM_PROBE] check iostat exist fail, popen error.\n");
        return -1;
    }
    line[0] = 0;
    if (fgets(line, LINE_BUF_LEN, f) == NULL) {
        printf("[SYSTEM_PROBE] iostat not exist, please install sysstat.\n");
        (void)pclose(f);
        return -1;
    }
    (void)pclose(f);

    /* obtain IO statistics */
    f = popen(SYSTEM_DISKSTATS_COMMAND, "r");
    if (f == NULL) {
        printf("[SYSTEM_PROBE] iostat fail, popen error.\n");
        return -1;
    }
    while (!feof(f)) {
        line[0] = 0;
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            break;
        }
        if (strstr(line, "Device") != NULL ||
            strstr(line, "::") != NULL) {
            continue;
        }
        SPLIT_NEWLINE_SYMBOL(line);
        split_line_to_substrings(line, pp, METRICS_IOSTAT_MAX);

        /* output */
        (void)fprintf(stdout, "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n",
            METRICS_IOSTAT_NAME,
            pp[METRICS_IOSTAT_DEVNAME],
            pp[METRICS_IOSTAT_RD_SPEED],
            pp[METRICS_IOSTAT_RDKB_SPEED],
            pp[METRICS_IOSTAT_RD_AWAIT],
            pp[METRICS_IOSTAT_RAREQ_SZ],
            pp[METRICS_IOSTAT_WR_SPEED],
            pp[METRICS_IOSTAT_WRKB_SPEED],
            pp[METRICS_IOSTAT_WR_AWAIT],
            pp[METRICS_IOSTAT_WAREQ_SZ],
            pp[METRICS_IOSTAT_UTIL]);
        /* output event */
        report_disk_iostat(pp, params);
    }
    (void)pclose(f);
    return 0;
}
