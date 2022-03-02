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
 * Description: system tcp&udp probe
 ******************************************************************************/
#include <stdio.h>
#include <string.h>

/*
 [root@master ~]# cat /proc/net/snmp | grep Tcp: | awk '{print $10 ":" $11 ":" $12 ":" $13 ":"  $14}' | tail -n1
 4:2413742:2164290:300:0
 [root@master ~]# cat /proc/net/snmp | grep Udp: | awk '{print $2 ":" $5}' | tail -n1
 1968:1968
*/

#define METRICS_NAME "system_tcp"
#define SYSTEM_SNMP_TCP_CMD \
    "/usr/bin/cat /proc/net/snmp | grep 'Tcp:' | tail -n1 | awk '{print $10 \":\" $11 \":\" $12 \":\" $13 \":\" $14}'"
#define SYSTEM_SNMP_UDP_CMD \
    "/usr/bin/cat /proc/net/snmp | grep 'Udp:' | tail -n1 | awk '{print $2 \":\" $5}'"
#define BUF_LEN     512
#define DATA_LEN    64

#define METRICS_TCP_CURR_ESTAB      0
#define METRICS_TCP_IN_SEGS         1
#define METRICS_TCP_OUT_SEGS        2
#define METRICS_TCP_RETRANS_SEGS    3
#define METRICS_TCP_IN_ERRS         4
#define METRICS_TCP_MAX             5
#define METRICS_UDP_IN_DATAGRAMS    0
#define METRICS_UDP_OUT_DATAGRAMS   1
#define METRICS_UDP_MAX             2

#define SPLIT_NEWLINE_SYMBOL(s) \
    do { \
        int __len = strlen(s); \
        if (__len > 0 && (s)[__len - 1] == '\n') { \
            (s)[__len - 1] = 0; \
        } \
    } while (0)

static int get_snmp_data(const char *cmd, char buf[][DATA_LEN], int max_len)
{
    int ret;
    FILE* f = NULL;
    char line[BUF_LEN];
    char* p;
    int index = 0;

    f = popen(cmd, "r");
    if (f == NULL) {
        return -1;
    }
    line[0] = 0;
    if (fgets(line, BUF_LEN, f) == NULL) {
        (void)pclose(f);
        return -1;
    }
    SPLIT_NEWLINE_SYMBOL(line);

    p = strtok(line, ":");
    while (p != NULL && index < max_len) {
    memset(buf[index], 0, DATA_LEN);
        strcpy(buf[index], p);
        p = strtok(NULL, ":");
        index++;
    }

    (void)pclose(f);
    return 0;
}

int main()
{
    int ret;
    char tcp_buf[METRICS_TCP_MAX][DATA_LEN];
    char udp_buf[METRICS_UDP_MAX][DATA_LEN];

    ret = get_snmp_data(SYSTEM_SNMP_TCP_CMD, tcp_buf, METRICS_TCP_MAX);
    if (ret < 0) {
        printf("system_tcp get tcp data error.\n");
        return -1;
    }
    ret = get_snmp_data(SYSTEM_SNMP_UDP_CMD, udp_buf, METRICS_UDP_MAX);
    if (ret < 0) {
        printf("system_tcp get udp data error.\n");
        return -1;
    }

    fprintf(stdout, "|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n",
        METRICS_NAME,
        "/proc/dev/snmp",
        tcp_buf[METRICS_TCP_CURR_ESTAB], 
        tcp_buf[METRICS_TCP_IN_SEGS], 
        tcp_buf[METRICS_TCP_OUT_SEGS], 
        tcp_buf[METRICS_TCP_RETRANS_SEGS], 
        tcp_buf[METRICS_TCP_IN_ERRS], 
        udp_buf[METRICS_UDP_IN_DATAGRAMS],
        udp_buf[METRICS_UDP_OUT_DATAGRAMS]);

    return 0;
}
