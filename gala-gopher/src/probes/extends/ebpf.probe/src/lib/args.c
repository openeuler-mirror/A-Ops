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
 * Author: Mr.lu
 * Create: 2021-10-18
 * Description: probe's args
 ******************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <getopt.h>

#include "args.h"

#define OUT_PUT_PERIOD_MAX     (120) // 2mim
#define OUT_PUT_PERIOD_MIN     (1)  // 1s

// gala-gopher.conf only support one arg, used set out put period
static int __period_arg_parse(char opt, char *arg, struct probe_params *params)
{
    unsigned int interval = 0;
    unsigned int flag = 0;

    if ((opt != 't' && opt != 'p' && opt != 'w' && opt != 'c') || arg == NULL)
        return -1;

    switch (opt) {
        case 't':
            interval = (unsigned int)atoi(arg);
            if (interval < OUT_PUT_PERIOD_MIN || interval > OUT_PUT_PERIOD_MAX) {
                printf("Please check arg(t), val shold inside 1~120.\n");
                return -1;
            }
            params->period = interval;
            break;
        case 'p':
            if (arg != NULL)
                (void)snprintf((void *)params->elf_path, MAX_PATH_LEN, "%s", arg);
            break;
        case 'w':
            if (arg != NULL)
                (void)snprintf((void *)params->task_whitelist, MAX_PATH_LEN, "%s", arg);
            break;
        case 'c':
            flag = (unsigned int)atoi(arg);
            if (flag != 0 && flag != 1) {
                printf("Please check arg(t), val shold be 1:cport_valid 0:cport_invalid.\n");
                return -1;
            }
            params->cport_flag = flag;
            break;
        default:
            break;
    }

    return 0;
}

static int __args_parse(int argc, char **argv, char *opt_str, struct probe_params *params)
{
    int ch = -1;

    if (opt_str == NULL)
        return -1;

    while ((ch = getopt(argc, argv, opt_str)) != -1) {
        if (!optarg)
            return -1;

        if (__period_arg_parse(ch, optarg, params) != 0)
            return -1;
    }
    return 0;
}

int args_parse(int argc, char **argv, char *opt_str, struct probe_params *params)
{
    return __args_parse(argc, argv, opt_str, params);
}

