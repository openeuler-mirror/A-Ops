/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
 */
#ifndef __GOPHER_ARGS_H__
#define __GOPHER_ARGS_H__

#define DEFAULT_PERIOD  5
#define MAX_PATH_LEN    512
struct probe_params {
    unsigned int period;
    char elf_path[MAX_PATH_LEN];
};
int args_parse(int argc, char **argv, char *opt_str, struct probe_params* params);

#endif
