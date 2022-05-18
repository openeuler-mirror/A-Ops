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
 * Description: system probe just in 1 thread, include tcp/net/iostat/inode
 ******************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include "args.h"


#define SYSTEM_PROBE_DESC(desc) 1

#define METRICS_TCP_NAME        "system_tcp"
#define METRICS_NET_NAME        "system_net"
#define METRICS_INODE_NAME      "system_inode"
#define METRICS_IOSTAT_NAME     "system_iostat"
#define SYSTEM_NET_SNMP_PATH    "/proc/net/snmp"
#define SYSTEM_NET_DEV_PATH     "/proc/net/dev"
#define SYSTEM_NETDEV_NUM       "/usr/bin/ls /sys/class/net | wc -l"
#define SYSTEM_INODE_COMMAND \
    "/usr/bin/df -i | awk 'NR>1 {print $1\"%\"$2\"%\"$3\"%\"$4\"%\"$5\"%\"$6}'"
#define IOSTAT_IS_EXIST         "which iostat"
#define SYSTEM_DISKSTATS_COMMAND \
    "iostat -xd | awk 'NR>1 {print $1\":\"$2\":\"$3\":\"$6\":\"$7\":\"$8\":\"$9\":\"$11\":\"$12\":\"$21}'"
#define LINE_BUF_LEN            512
#define NET_DEVICE_NAME_SIZE    16
#define DATA_LEN                64

#define METRICS_INODE_FSYS_TYPE     0
#define METRICS_INODE_INODES        1
#define METRICS_INODE_IUSED         2
#define METRICS_INODE_IFREE         3
#define METRICS_INODE_IUSE_PER      4
#define METRICS_INODE_MOUNTED       5
#define METRICS_INODE_MAX           6

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

typedef struct net_snmp_stat {
    unsigned long long tcp_curr_estab;
    unsigned long long tcp_in_segs;
    unsigned long long tcp_out_segs;
    unsigned long long tcp_retrans_segs;
    unsigned long long tcp_in_errs;
    unsigned long long udp_in_datagrams;
    unsigned long long udp_out_datagrams;
} net_snmp_stat;

typedef struct net_dev_stat {
    char dev_name[NET_DEVICE_NAME_SIZE];
    unsigned long long rx_bytes;
    unsigned long long rx_packets;
    unsigned long long rx_dropped;
    unsigned long long rx_errs;
    unsigned long long rx_fifo_errs;
    unsigned long long rx_frame_errs;
    unsigned long long rx_compressed;
    unsigned long long rx_multicast;
    unsigned long long tx_packets;
    unsigned long long tx_dropped;
    unsigned long long tx_bytes;
    unsigned long long tx_errs;
    unsigned long long tx_fifo_errs;
    unsigned long long tx_colls;
    unsigned long long tx_carrier;
    unsigned long long tx_compressed;
} net_dev_stat;

/*
 [root@master ~]# cat /proc/net/snmp | grep Tcp: | awk '{print $10 ":" $11 ":" $12 ":" $13 ":"  $14}' | tail -n1
 4:2413742:2164290:300:0
 [root@master ~]# cat /proc/net/snmp | grep Udp: | awk '{print $2 ":" $5}' | tail -n1
 1968:1968
 */
#if SYSTEM_PROBE_DESC("system tcp probe")
static void get_netsnmp_fileds(const char *net_snmp_info, net_snmp_stat *stats)
{
    int ret;
    char *colon = strchr(net_snmp_info, ':');
    if (colon == NULL) {
        printf("net_snmp not find symbol ':' \n");
        return;
    }
    *colon = '\0';

    if (strcmp(net_snmp_info, "Tcp") == 0) {
        ret = sscanf(colon + 1,
            "%*Lu %*Lu %*Lu %*Lu %*Lu %*Lu %*Lu %*Lu %llu %llu %llu %llu %llu",
            &stats->tcp_curr_estab, &stats->tcp_in_segs, &stats->tcp_out_segs,
            &stats->tcp_retrans_segs, &stats->tcp_in_errs);
        return;
    }
    if (strcmp(net_snmp_info, "Udp") == 0) {
        ret = sscanf(colon + 1, "%llu %*Lu %*Lu %llu",
            &stats->udp_in_datagrams, &stats->udp_out_datagrams);
        return;
    }
    return;
}

static int system_tcp_probe(net_snmp_stat *stats)
{
    FILE* f = NULL;
    char line[LINE_BUF_LEN];
    net_snmp_stat temp = {0};
    int ret;

    f = fopen(SYSTEM_NET_SNMP_PATH, "r");
    if (f == NULL) {
        return -1;
    }
    /* fopen success, copy stats to temp */
    (void)memcpy(&temp, stats, sizeof(net_snmp_stat));

    /* parse lines */
    while (!feof(f)) {
        (void)memset(line, 0, LINE_BUF_LEN);
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            break;
        }
        get_netsnmp_fileds(line, stats);
    }
    /* output */
    fprintf(stdout, "|%s|%s|%llu|%llu|%llu|%llu|%llu|%llu|%llu|\n",
        METRICS_TCP_NAME,
        "/proc/dev/snmp",
        stats->tcp_curr_estab,
        stats->tcp_in_segs - temp.tcp_in_segs,
        stats->tcp_out_segs - temp.tcp_out_segs,
        stats->tcp_retrans_segs - temp.tcp_retrans_segs,
        stats->tcp_in_errs - temp.tcp_in_errs,
        stats->udp_in_datagrams - temp.udp_in_datagrams,
        stats->udp_out_datagrams - temp.udp_out_datagrams);

    (void)fclose(f);
    return 0;
}
#endif

/*
 [root@ecs-ee4b-0019 ~]# cat /proc/net/dev
 Inter-|   Receive                                                |  Transmit
  face |   bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
  eth0: 58324993484 49590277  0    0    0    0       0         0   26857829724 19952463  0    0    0    0      0      0
    lo:  878352945  6861344   0    0    0    0       0         0    878352945  6861344   0    0    0    0      0      0
 */
#if SYSTEM_PROBE_DESC("system net probe")
static int get_netdev_num(int *num)
{
    FILE *f = NULL;
    char line[LINE_BUF_LEN];

    f = popen(SYSTEM_NETDEV_NUM, "r");
    if (f == NULL) {
        printf("[SYSTEM_PROBE] ls fail, popen error.\n");
        return -1;
    }
    if (fgets(line, LINE_BUF_LEN, f) == NULL) {
        (void)pclose(f);
        return -1;
    }
    SPLIT_NEWLINE_SYMBOL(line);
    *num = atoi(line);
    (void)pclose(f);
    return 0;
}

static void get_netdev_fileds(const char *net_dev_info, net_dev_stat *stats)
{
    int ret;
    char *devinfo = (char *)net_dev_info;

    char *colon = strchr(devinfo, ':');
    if (colon == NULL) {
        printf("system_net.probe not find symbol ':' \n");
        return;
    }
    *colon = '\0';

    (void)snprintf((char *)stats->dev_name, NET_DEVICE_NAME_SIZE, devinfo);
    ret = sscanf(colon + 1,
        "%llu %llu %llu %llu %*Lu %*Lu %*Lu %*Lu %llu %llu %llu %llu %*Lu %*Lu %*Lu %*Lu",
        &stats->rx_bytes, &stats->rx_packets, &stats->rx_errs, &stats->rx_dropped,
        &stats->tx_bytes, &stats->tx_packets, &stats->tx_errs, &stats->tx_dropped);
    if (ret < 8) {
        printf("system_net.probe faild get net_dev metrics.\n");
    }
    return;
}

static int system_net_probe(net_dev_stat *stats, int num)
{
    FILE* f = NULL;
    char line[LINE_BUF_LEN];
    net_dev_stat temp;
    int i, ret;
    int index = 0;

    f = fopen(SYSTEM_NET_DEV_PATH, "r");
    if (f == NULL) {
        return -1;
    }
    while (!feof(f)) {
        (void)memset(line, 0, LINE_BUF_LEN);
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            fclose(f);
            return 0;
        }
        if (strstr(line, "Inter") != NULL ||
            strstr(line, "face") != NULL ||
            strstr(line, "lo") != NULL) {
            continue;
        }
        for (i = 0; line[i] != '\0'; i++) {
            if (line[i] != ' ') {
                break;
            }
        }
        if (index >= num) {
            printf("[SYSTEM_PROBE] net_probe record beyond max nums(%d).\n", num);
            return -1;
        }
        (void)memcpy(&temp, &stats[index], sizeof(net_dev_stat));
        get_netdev_fileds(line + i, &stats[index]);
        fprintf(stdout, "|%6s|%s|%llu|%llu|%llu|%llu|%llu|%llu|%llu|%llu|\n",
            METRICS_NET_NAME,
            stats[index].dev_name,
            stats[index].rx_bytes - temp.rx_bytes,
            stats[index].rx_packets - temp.rx_packets,
            stats[index].rx_errs - temp.rx_errs,
            stats[index].rx_dropped - temp.rx_dropped,
            stats[index].tx_bytes - temp.tx_bytes,
            stats[index].tx_packets - temp.tx_packets,
            stats[index].tx_errs - temp.tx_errs,
            stats[index].tx_dropped - temp.tx_dropped);
        index++;
    }

    (void)fclose(f);
    return 0;
}
#endif

/*
 [root@k8s-node2 net]# /usr/bin/df -i | awk 'NR>1 {print $1"%"$2"%"$3"%"$4"%"$5"%"$6}'
 Inodes:IUsed:IFree:IUse
 65536:413:65123:1%
 */
#if SYSTEM_PROBE_DESC("system inode probe")
static int system_inode_probe()
{
    FILE *f = NULL;
    char line[LINE_BUF_LEN];
    int index;
    char *p;
    char *pp[METRICS_INODE_MAX];

    f = popen(SYSTEM_INODE_COMMAND, "r");
    if (f == NULL) {
        printf("[SYSTEM_PROBE] /user/bin/df fail, popen error.\n");
        return -1;
    }
    while (!feof(f)) {
        (void)memset(line, 0, LINE_BUF_LEN);
        index = 0;
        if (NULL == fgets(line, LINE_BUF_LEN, f)) {
            break;
        }
        p = strtok(line, "%");
        while (p != NULL && index < METRICS_INODE_MAX) {
            pp[index++] = p;
            p = strtok(NULL, "%");
        }
        *(pp[METRICS_INODE_MOUNTED] + DATA_LEN - 1) = '\0';
        SPLIT_NEWLINE_SYMBOL(pp[METRICS_INODE_MOUNTED]);
        /* output */
        fprintf(stdout, "|%s|%s|%s|%s|%s|%s|%s|\n",
            METRICS_INODE_NAME,
            pp[METRICS_INODE_MOUNTED],
            pp[METRICS_INODE_FSYS_TYPE],
            pp[METRICS_INODE_INODES],
            pp[METRICS_INODE_IUSE_PER],
            pp[METRICS_INODE_IUSED],
            pp[METRICS_INODE_IFREE]);
    }
    (void)pclose(f);
    return 0;
}
#endif

/*
 [root@localhost ~]# iostat -xd -t 5
 Device r/s rkB/s r_await rareq-sz w/s wkB/s w_await wareq-sz d/s  dkB/s drqm/s %drqm d_await dareq-sz aqu-sz %util
  sda  0.28 19.59  0.58    68.93  1.69 65.02  0.81    38.57  0.00  0.00  0.00   0.00   0.00     0.00    0.00  0.09
 */
#if SYSTEM_PROBE_DESC("system iostat probe")
static int system_iostat_probe()
{
    FILE* f = NULL;
    char line[LINE_BUF_LEN];
    int index;
    char *p;
    char *pp[METRICS_IOSTAT_MAX];

    line[0] = 0;
    /* check whether iostat is installed in this OS */
    f = popen(IOSTAT_IS_EXIST, "r");
    if (f == NULL) {
        printf("[SYSTEM_PROBE] check iostat exist fail, popen error.\n");
        return -1;
    }
    if (fgets(line, LINE_BUF_LEN, f) == NULL) {
        printf("[SYSTEM_PROBE] iostat not exist, please install sysstat.\n");
        (void)pclose(f);
        return -1;
    }
    (void)pclose(f);

    /* obtain IO statistics */
    f = popen(SYSTEM_DISKSTATS_COMMAND, "r");
    if (f ==NULL) {
        printf("[SYSTEM_PROBE] iostat fail, popen error.\n");
        return -1;
    }
    while (!feof(f)) {
        (void)memset(line, 0, LINE_BUF_LEN);
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            break;
        }
        if (strstr(line, "Device") != NULL ||
            strstr(line, "::") != NULL) {
            continue;
        }
        SPLIT_NEWLINE_SYMBOL(line);

        p = strtok(line, ":");
        index = 0;
        while (p != NULL && index < METRICS_IOSTAT_MAX) {
            pp[index++] = p;
            p = strtok(NULL, ":");
        }
        /* output */
        fprintf(stdout, "|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n",
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
    }
    (void)pclose(f);
    return 0;
}
#endif

int main(struct probe_params * params)
{
    int ret, num = 0;
    net_snmp_stat snmp_stats = {0};
    net_dev_stat *dev_stats;

    ret = get_netdev_num(&num);
    if (ret < 0 || num <= 0) {
        return -1;
    }
    dev_stats = (net_dev_stat *)malloc(num * sizeof(net_dev_stat));
    if (dev_stats == NULL) {
        return -1;
    }
    (void)memset(dev_stats, 0, num * sizeof(net_dev_stat));

    for (;;) {
        ret = system_tcp_probe(&snmp_stats);
        if (ret < 0) {
            printf("[SYSTEM_PROBE] system tcp probe fail.\n");
            goto err;
        }
        ret = system_net_probe(dev_stats, num);
        if (ret < 0) {
            printf("[SYSTEM_PROBE] system net probe fail.\n");
            goto err;
        }
        ret = system_inode_probe();
        if (ret < 0) {
            printf("[SYSTEM_PROBE] system inode probe fail.\n");
            goto err;
        }
        ret = system_iostat_probe();
        if (ret < 0) {
            printf("[SYSTEM_PROBE] system iostat probe fail.\n");
            goto err;
        }
        sleep(params->period);
    }

err:
    if (dev_stats != NULL) {
        (void)free(dev_stats);
        dev_stats = NULL;
    }
    return -1;
}
