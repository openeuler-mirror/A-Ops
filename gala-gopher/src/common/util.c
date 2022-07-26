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
 * Author: sky
 * Create: 2021-05-22
 * Description: lib module
 ******************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <signal.h>
#include <unistd.h>
#include <string.h>
#include <stdarg.h>
#include "common.h"

char *get_cur_time(void)
{
    /* return time str, ex: 2021/5/17 19:56:03 */
    static char tm[TM_STR_LEN] = {0};
    struct tm *tmp_ptr = NULL;
    time_t t;

    (void)time(&t);

    tmp_ptr = localtime(&t);
    (void)snprintf(tm,
        TM_STR_LEN,
        "%d/%d/%d %02d:%02d:%02d",
        (1900 + tmp_ptr->tm_year),
        (1 + tmp_ptr->tm_mon),
        tmp_ptr->tm_mday,
        tmp_ptr->tm_hour,
        tmp_ptr->tm_min,
        tmp_ptr->tm_sec);
    return tm;
}

void ip6_str(unsigned char *ip6, unsigned char *ip_str, unsigned int ip_str_size)
{
    unsigned short *addr = (unsigned short *)ip6;
    int i, j;
    char str[48];
    /* 1. format ipv6 address */
    (void)snprintf((char *)str, ip_str_size, NIP6_FMT, NIP6(addr));
    /* 2. compress */
    for (i = 0, j = 0; str[j] != '\0'; i++, j++) {
        if (str[j] == '0' && (j == 0 || ip_str[i - 1] == ':')) {  // the first 0
            if (str[j + 1] != '0') {        // 0XXX
                j = j + 1;
            } else if (str[j + 2]!='0') {   // 00XX
                j = j + 2;
            } else {                        // 000X 0000
                j = j + 3;
            }
        }
        ip_str[i] = str[j];
    }
    ip_str[i] = '\0';
    return;
}

void ip_str(unsigned int family, unsigned char *ip, unsigned char *ip_str, unsigned int ip_str_size)
{
    ip_str[0] = 0;
    
    if (family == AF_INET6) {
        (void)ip6_str(ip, ip_str, ip_str_size);
        return;
    }

    (void)snprintf((char *)ip_str, ip_str_size, "%u.%u.%u.%u", ip[0], ip[1], ip[2], ip[3]);
    return;
}

void split_newline_symbol(char *s)
{
    int len = strlen(s);
    if (len > 0 && s[len - 1] == '\n') {
        s[len - 1] = 0;
    }
}

char is_exist_mod(const char *mod)
{
    int cnt = 0;
    FILE *fp;
    char cmd[COMMAND_LEN];
    char line[LINE_BUF_LEN];

    cmd[0] = 0;
    (void)snprintf(cmd, COMMAND_LEN, "lsmod | grep -w %s | wc -l", mod);
    fp = popen(cmd, "r");
    if (fp == NULL) {
        return 0;
    }

    line[0] = 0;
    if (fgets(line, LINE_BUF_LEN, fp) != NULL) {
        SPLIT_NEWLINE_SYMBOL(line);
        cnt = atoi(line);
    }
    pclose(fp);

    return (char)(cnt > 0);
}

int exec_cmd(const char *cmd, char *buf, unsigned int buf_len)
{
    FILE *f = NULL;

    f = popen(cmd, "r");
    if (f == NULL)
        return -1;

    if (fgets(buf, buf_len, f) == NULL) {
        (void)pclose(f);
        return -1;
    }
    (void)pclose(f);

    SPLIT_NEWLINE_SYMBOL(buf);
    return 0;
}

int __snprintf(char **buf, const int bufLen, int *remainLen, const char *format, ...)
{
    int len;
    char *p = *buf;
    va_list args;

    if (bufLen <= 0) {
        return -1;
    }

    va_start(args, format);
    len = vsnprintf(p, (const unsigned int)bufLen, format, args);
    va_end(args);

    if (len >= bufLen || len < 0) {
        return -1;
    }

    *buf += len;
    *remainLen = bufLen - len;

    return 0;
}