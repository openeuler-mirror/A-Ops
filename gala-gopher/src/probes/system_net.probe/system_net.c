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
 * Create: 2022-02-28
 * Description: system net_dev probe
 ******************************************************************************/
#include <stdio.h>
#include <string.h>

/*
eg:
[root@ecs-ee4b-0019 ~]# cat /proc/net/dev
Inter-|   Receive                                                |  Transmit
 face |   bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
 eth0: 58324993484 49590277  0    0    0    0       0         0   26857829724 19952463  0    0    0     0       0          0
   lo:  878352945  6861344   0    0    0    0       0         0    878352945  6861344   0    0    0     0       0          0
*/

#define METRICS_NAME            "system_net"
#define SYSTEM_NET_DEV_PATH     "/proc/net/dev"
#define LINE_BUF_LEN            512
#define NET_DEVICE_NAME_SIZE    16

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

static void get_netdev_fileds(const char *net_dev_info, net_dev_stat *stats)
{
    int ret;

    ret = sscanf(net_dev_info,
        "%s: %llu %llu %llu %llu %*Lu %*Lu %*Lu %*Lu %llu %llu %llu %llu %*Lu %*Lu %*Lu %*Lu",
        &stats->dev_name,
        &stats->rx_bytes, &stats->rx_packets, &stats->rx_errs, &stats->rx_dropped,
        &stats->tx_bytes, &stats->tx_packets, &stats->tx_errs, &stats->tx_dropped);

    if (ret < 9) {
        printf("system_net.probe faild get net_dev info.\n");
    }
    return;
}

int main()
{
    FILE* f = NULL;
    char line[LINE_BUF_LEN];
    net_dev_stat stats;

    f = fopen(SYSTEM_NET_DEV_PATH, "r");
    if (f == NULL) {
        return -1;
    }
    while (!feof(f)) {
        (void)memset(line, 0, LINE_BUF_LEN);
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            fclose(f);
            return -1;
        }
    if (strstr(line, "Inter") != NULL ||
        strstr(line, "face") != NULL ||
        strstr(line, "lo") != NULL) {
        continue;
    }
        get_netdev_fileds(line, &stats);
        fprintf(stdout,
            "|%6s|%s|%llu|%llu|%llu|%llu|%llu|%llu|%llu|%llu|\n",
            METRICS_NAME,
            stats.dev_name,
            stats.rx_bytes,
            stats.rx_packets,
            stats.rx_errs,
            stats.rx_dropped,
            stats.tx_bytes,
            stats.tx_packets,
            stats.tx_errs,
            stats.tx_dropped);
    }
    (void)fclose(f);
    return 0;
}
