/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
 */
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <getopt.h>

#include "args.h"

#define OUT_PUT_PERIOD_MAX     (120) // 2mim
#define OUT_PUT_PERIOD_MIN     (1)  // 1s

// gala-gopher.conf only support one arg, used set out put period
int __period_arg_parse(char opt, char *arg, struct probe_params *params)
{
    unsigned int interval = 0;

    if ((opt != 't' && opt != 'p') || arg == NULL) {
        return -1;
    }

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
            if (arg != NULL) {
                (void)snprintf((void *)params->elf_path, MAX_PATH_LEN, "%s", arg);
            }
            break;
        default:
            break;
    }

    return 0;
}

int __args_parse(int argc, char **argv, char *opt_str, struct probe_params *params)
{
    int ch = -1;

    if (opt_str == NULL) {
        return -1;
    }
    while ((ch = getopt(argc, argv, opt_str)) != -1) {
        if (!optarg) {
            return -1;
        }
        if (__period_arg_parse(ch, optarg, params) != 0) {
            return -1;
        }
    }
    return 0;
}

int args_parse(int argc, char **argv, char *opt_str, struct probe_params *params)
{
    return __args_parse(argc, argv, opt_str, params);
}

