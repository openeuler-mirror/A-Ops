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
#include "event.h"
#include "system_disk.h"

#define METRICS_DISK_NAME       "system_disk"
#define METRICS_IOSTAT_NAME     "system_iostat"
#define SYSTEM_INODE_COMMAND \
    "/usr/bin/df -i | /usr/bin/awk 'NR>1 {print $1\"%\"$2\"%\"$3\"%\"$4\"%\"$5\"%\"$6}'"
#define SYSTEM_BLOCK_CMD \
    "/usr/bin/df | /usr/bin/awk '{if($6==\"%s\"){print $1\"%\"$2\"%\"$3\"%\"$4\"%\"$5\"%\"$6}}'"
#define SYSTEM_DISKSTATS_CMD    "/usr/bin/cat /proc/diskstats"
#define SYSTEM_DISK_DEV_NUM     "/usr/bin/cat /proc/diskstats | wc -l"

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
                    "Too many Inodes consumed(%d%%).",
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
                    "Too many Blocks used(%d%%).",
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

static int get_diskstats_fields(const char *line, disk_stats *stats)
{
    int ret;

    ret = sscanf(line,
        "%*Lu %*Lu %s %lu %*Lu %lu %u %lu %*Lu %lu %u %*Lu %u %*Lu %*Lu %*Lu %*Lu %*Lu",
        &stats->disk_name, &stats->rd_ios, &stats->rd_sectors, &stats->rd_ticks,
        &stats->wr_ios, &stats->wr_sectors, &stats->wr_ticks, &stats->io_ticks);
    if (ret < 8) {
        printf("[SYSTEM_PROBE] get disk stats fields fail.\n");
        return -1;
    }
    return 0;
}

static void cal_disk_io_stats(disk_stats *last, disk_stats *cur, disk_io_stats *io_info, const int period)
{
    if (cur->rd_ios - last->rd_ios == 0) {
        io_info->rd_await = 0.0;
        io_info->rareq_sz = 0.0;
    } else {
        io_info->rd_await = (cur->rd_ticks - last->rd_ticks) / ((double)(cur->rd_ios - last->rd_ios));
        io_info->rareq_sz = (cur->rd_sectors - last->rd_sectors) / ((double)(cur->rd_ios - last->rd_ios)) / 2;
    }
    if (cur->wr_ios - last->wr_ios == 0) {
        io_info->wr_await = 0.0;
        io_info->wareq_sz = 0.0;
    } else {
        io_info->wr_await = (cur->wr_ticks - last->wr_ticks) / ((double)(cur->wr_ios - last->wr_ios));
        io_info->wareq_sz = (cur->wr_sectors - last->wr_sectors) / ((double)(cur->wr_ios - last->wr_ios)) / 2;
    }

    io_info->rd_speed = S_VALUE(last->rd_ios, cur->rd_ios, period);
    io_info->wr_speed = S_VALUE(last->wr_ios, cur->wr_ios, period);

    io_info->rdkb_speed = S_VALUE(last->rd_sectors, cur->rd_sectors, period) / 2;
    io_info->wrkb_speed = S_VALUE(last->wr_sectors, cur->wr_sectors, period) / 2;

    io_info->util = S_VALUE(last->io_ticks, cur->io_ticks, period) / 10.0;

    return;
}

static void report_disk_iostat(const char *disk_name, disk_io_stats *io_info, struct probe_params *params)
{
    char entityid[LINE_BUF_LEN];

    if (params->logs == 0) {
        return;
    }

    entityid[0] = 0;

    if (io_info->util > params->res_percent_upper) {
        (void)strncpy(entityid, disk_name, LINE_BUF_LEN - 1);
        report_logs(METRICS_IOSTAT_NAME,
                    entityid,
                    "iostat_util",
                    EVT_SEC_WARN,
                    "Disk device saturated(%.2f%%).",
                    io_info->util);
    }
}

/*
 [root@localhost ~]# iostat -xd -t 60
 Device r/s rkB/s r_await rareq-sz w/s wkB/s w_await wareq-sz d/s dkB/s drqm/s %drqm d_await dareq-sz aqu-sz %util
  sda  0.28 19.59  0.58    68.93  1.69 65.02  0.81    38.57  0.00  0.00  0.00  0.00   0.00     0.00    0.00  0.09

 [root@localhost ~]# cat /proc/diskstats
   8       0 sda 28113 601 3643572 9344 119389 109397 12096368 103830 0 98049 69319 0 0 0 0
                  3          5      6     7              9       10       12
 */
static disk_stats *g_disk_stats = NULL;
static int g_disk_dev_num;
static int g_first_flag;

int system_iostat_probe(struct probe_params *params)
{
    FILE *f = NULL;
    char line[LINE_BUF_LEN];
    disk_stats temp;
    disk_io_stats io_datas;
    int index;

    f = popen(SYSTEM_DISKSTATS_CMD, "r");
    if (f == NULL) {
        return -1;
    }

    index = 0;
    while (!feof(f) && index < g_disk_dev_num) {
        line[0] = 0;
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            (void)pclose(f);
            return -1;
        }
        (void)memcpy(&temp, &g_disk_stats[index], sizeof(disk_stats));
        (void)get_diskstats_fields(line, &g_disk_stats[index]);

        if (g_first_flag == 1) {
            (void)memset(&io_datas, 0, sizeof(disk_io_stats));
        } else {
            cal_disk_io_stats(&temp, &g_disk_stats[index], &io_datas, params->period);
        }

        (void)fprintf(stdout,
            "|%s|%s|%.2f|%.2f|%.2f|%.2f|%.2f|%.2f|%.2f|%.2f|%.2f|\n",
            METRICS_IOSTAT_NAME,
            g_disk_stats[index].disk_name,
            io_datas.rd_speed,
            io_datas.rdkb_speed,
            io_datas.rd_await,
            io_datas.rareq_sz,
            io_datas.wr_speed,
            io_datas.wrkb_speed,
            io_datas.wr_await,
            io_datas.wareq_sz,
            io_datas.util);
        /* event_output */
        report_disk_iostat(g_disk_stats[index].disk_name, &io_datas, params);

        index++;
    }
    g_first_flag = 0;
    (void)pclose(f);
    return 0;
}

static int get_diskdev_num(int *num)
{
    FILE *f = NULL;
    char line[LINE_BUF_LEN];

    f = popen(SYSTEM_DISK_DEV_NUM, "r");
    if (f == NULL) {
        return -1;
    }
    line[0] = 0;
    if (fgets(line, LINE_BUF_LEN, f) == NULL) {
        (void)pclose(f);
        return -1;
    }
    SPLIT_NEWLINE_SYMBOL(line);
    *num = atoi(line);
    (void)pclose(f);
    return 0;
}

int system_iostat_init(void)
{
    int ret = get_diskdev_num(&g_disk_dev_num);
    if (ret < 0 || g_disk_dev_num <= 0) {
        return -1;
    }
    g_disk_stats = malloc(g_disk_dev_num * sizeof(disk_stats));
    if (g_disk_stats == NULL) {
        return -1;
    }
    (void)memset(g_disk_stats, 0, g_disk_dev_num * sizeof(disk_stats));

    g_first_flag = 1;

    return 0;
}

void system_iostat_destroy(void)
{
    while (g_disk_stats != NULL) {
        (void)free(g_disk_stats);
        g_disk_stats = NULL;
    }
    return;
}