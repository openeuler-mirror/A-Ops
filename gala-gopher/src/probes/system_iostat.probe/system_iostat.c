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

/*
[root@localhost ~]# iostat -xd -t 60
Device r/s rkB/s rrqm/s %rrqm r_await rareq-sz w/s wkB/s wrqm/s %wrqm w_await wareq-sz d/s dkB/s drqm/s %drqm d_await dareq-sz aqu-sz %util
 sda  0.28 19.59  0.00  0.00   0.58    68.93  1.69 65.02  0.00   0.00  0.81    38.57  0.00  0.00  0.00  0.00   0.00     0.00    0.00  0.09

[root@localhost ~]# cat /proc/diskstats
   8       0 sda 28113 601 3643572 9344 119389 109397 12096368 103830 0 98049 69319 0 0 0 0
                  3          5      6     7              9       10       12
*/

#define METRICS_NAME            "system_iostat"
#define SYSTEM_DISKSTATS_COMMAND   "/usr/bin/cat /proc/diskstats | grep -w %s"
#define LOCAL_DISK_COMMAND      "ls -l /sys/block/ | grep pci | awk -F \"/\" '{print $NF}'"
#define DISK_DEV_NAME_SIZE      32
#define MAX_LOCAL_DISK_NUM      10
#define LINE_BUF_LEN            256

#define SPLIT_NEWLINE_SYMBOL(s) \
    do { \
        int __len = strlen(s); \
        if (__len > 0 && (s)[__len - 1] == '\n') { \
            (s)[__len - 1] = 0; \
        } \
    } while (0)

typedef struct _disk_stats {
    // unsigned int major;
    // unsigned int minor;
    // char disk_name[DISK_DEV_NAME_SIZE];
    unsigned long rd_ios;
    // unsigned long rd_merges;
    unsigned long rd_sectors;
    unsigned int rd_ticks;
    unsigned long wr_ios;
    // unsigned long wr_merges;
    unsigned long wr_sectors;
    unsigned int wr_ticks;
    // unsigned int in_flight;
    unsigned int io_ticks;
    // unsigned int time_in_queue;
    // unsigned long discard_ios;
    // unsigned long discard_merges;
    // unsigned long discard_sectors;
    // unsigned int discard_ticks;
} disk_stats;

typedef struct _disk_io_stats {
    float rd_speed;
    float rdkb_speed;
    float rd_await;
    float rareq_sz;
    float wr_speed;
    float wrkb_speed;
    float wr_await;
    float wareq_sz;
    float util;
} disk_io_stats;

typedef struct _local_disk {
    struct _local_disk *next;
    char disk_name[DISK_DEV_NAME_SIZE];
    disk_stats stats_info1;       // first time
    disk_stats stats_info2;       // second time
    disk_io_stats disk_io_info;
} local_disk;

#define LIST_FOR_EACH(list_head, list_node) \
    for ((list_node) = (list_head)->next; \
         (list_node) != NULL; \
         (list_node) = (list_node)->next)

static int g_period = 60;    // 60s = 1min

static int local_disk_add(local_disk *local_disk_head)
{
    FILE *fp = NULL;
    char line[LINE_BUF_LEN];
    local_disk *disk = NULL;

    fp = popen(LOCAL_DISK_COMMAND, "r");
    if (fp == NULL) {
        printf("[SYSTEM_IOSTAT] cmd: ls /sys/block popen fail, %s with %d. \n", strerror(errno), errno);
        return -1;
    }
    while (!feof(fp)) {
        (void)memset(line, 0, LINE_BUF_LEN);
        if (fgets(line, LINE_BUF_LEN, fp) == NULL) {
            break;
        }
        SPLIT_NEWLINE_SYMBOL(line);
        disk = malloc(sizeof(local_disk));
        (void)memset(disk, 0, sizeof(local_disk));
        (void)strcpy(disk->disk_name, line);

        disk->next = local_disk_head->next;
        local_disk_head->next = disk;
    }
    pclose(fp);
    return 0;
}

static void free_local_disk(local_disk *disklist)
{
    local_disk *tmp_disk = NULL;

    while (disklist != NULL) {
        tmp_disk = disklist->next;
        free(disklist);
        disklist = tmp_disk;
    }
    return;
}

static int parse_stats(const char *line, disk_stats *stats)
{
    int ret;

    ret = sscanf(line,
        "%*Lu %*Lu %*s %lu %*Lu %lu %u %lu %*Lu %lu %u %*Lu %u %*Lu %*Lu %*Lu %*Lu %*Lu",
        &stats->rd_ios, &stats->rd_sectors, &stats->rd_ticks,
        &stats->wr_ios, &stats->wr_sectors, &stats->wr_ticks, &stats->io_ticks);

    if (ret < 7) {
        printf("[SYSTEM_IOSTAT] faild to parse diskstats info.\n");
    }
    return ret;
}

static int get_disk_stats(local_disk *local_disk_head, const int get_id)
{
    FILE* f = NULL;
    char line[LINE_BUF_LEN];
    char cmd[LINE_BUF_LEN];
    char diskname[DISK_DEV_NAME_SIZE];
    local_disk *disk = NULL;
    int ret;

    LIST_FOR_EACH(local_disk_head, disk) {
        memset(cmd, 0, LINE_BUF_LEN);
        (void)snprintf(cmd, LINE_BUF_LEN, SYSTEM_DISKSTATS_COMMAND, disk->disk_name);
        f = popen(cmd, "r");
        if (f == NULL) {
            printf("[SYSTEM_IOSTAT] the %d time get disk[%s] stats fail, popen error.\n", get_id, disk->disk_name);
            return -1;
        }
        (void)memset(line, 0, LINE_BUF_LEN);
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            printf("[SYSTEM_IOSTAT] the %d time get disk[%s] stats fail, fgets error.\n", get_id, disk->disk_name);
            pclose(f);
            return -1;
        }
        if (get_id == 1) {
            (void)parse_stats((const char*)line, &disk->stats_info1);
        } else if (get_id == 2) {
            (void)parse_stats((const char*)line, &disk->stats_info2);
        } else {
            ;
        }
        (void)pclose(f);
    }
    return 0;
}

static int get_disk_io_info(local_disk *disk_node)
{
    disk_stats *first = NULL;
    disk_stats *second = NULL;
    disk_io_stats *io_info = NULL;

    if (disk_node == NULL) {
        return -1;
    }
    first = &disk_node->stats_info1;
    second = &disk_node->stats_info2;
    io_info = &disk_node->disk_io_info;

    if (second->rd_ios - first->rd_ios == 0) {
        io_info->rd_await = 0.0;
        io_info->rareq_sz = 0.0;
    } else {
        io_info->rd_await = (second->rd_ticks - first->rd_ticks) / ((double)(second->rd_ios - first->rd_ios));
        io_info->rareq_sz = (second->rd_sectors - first->rd_sectors) / ((double)(second->rd_ios - first->rd_ios)) / 2;
    }
    if (second->wr_ios - first->wr_ios == 0) {
        io_info->wr_await = 0.0;
        io_info->wareq_sz = 0.0;
    } else {
        io_info->wr_await = (second->wr_ticks - first->wr_ticks) / ((double)(second->wr_ios - first->wr_ios));
        io_info->wareq_sz = (second->wr_sectors - first->wr_sectors) / ((double)(second->wr_ios - first->wr_ios)) / 2;
    }

    io_info->rd_speed = ((double)(second->rd_ios - first->rd_ios)) / g_period;
    io_info->wr_speed = ((double)(second->wr_ios - first->wr_ios)) / g_period;

    io_info->rdkb_speed = ((double)(second->rd_sectors - first->rd_sectors)) / g_period / 2;
    io_info->wrkb_speed = ((double)(second->wr_sectors - first->wr_sectors)) / g_period / 2;

    io_info->util = ((double)(second->io_ticks - first->io_ticks)) / g_period;

    return 0;
}

int main()
{
    int ret;
    local_disk *disk_head = NULL;

    disk_head = malloc(sizeof(local_disk));
    if (disk_head == NULL) {
        printf("[SYSTEM_IOSTAT] malloc local_disk head fail.\n");
        return -1;
    }
    disk_head->next = NULL;

    /* add locak disks */
    ret = local_disk_add(disk_head);
    if (ret != 0) {
        printf("[SYSTEM_IOSTAT] add system's local disk fail.\n");
        goto out;
    }

    /* get disk stats first time */
    ret = get_disk_stats(disk_head, 1);
    if (ret < 0) {
        goto out;
    }

    /* sleep 1min */
    (void)sleep(g_period);

    /* get dis stats second time */
    ret = get_disk_stats(disk_head, 2);
    if (ret < 0) {
        goto out;
    }

    local_disk *disk_node = NULL;
    LIST_FOR_EACH(disk_head, disk_node) {
        /* calcu iostat */
        (void)get_disk_io_info(disk_node);
        /* output */
        fprintf(stdout,
            "|%s|%s|%.2f|%.2f|%.2f|%.2f|%.2f|%.2f|%.2f|%.2f|%.2f|\n",
            METRICS_NAME,
            disk_node->disk_name,
            disk_node->disk_io_info.rd_speed,
            disk_node->disk_io_info.rdkb_speed,
            disk_node->disk_io_info.rd_await,
            disk_node->disk_io_info.rareq_sz,
            disk_node->disk_io_info.wr_speed,
            disk_node->disk_io_info.wrkb_speed,
            disk_node->disk_io_info.wr_await,
            disk_node->disk_io_info.wareq_sz,
            disk_node->disk_io_info.util);
    }

out:
    free_local_disk(disk_head);
    return 0;
}
