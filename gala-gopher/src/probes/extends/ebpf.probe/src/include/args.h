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
 * Description: probe's arg header
 ******************************************************************************/
#ifndef __GOPHER_ARGS_H__
#define __GOPHER_ARGS_H__

#define DEFAULT_PERIOD  5
#define MAX_PATH_LEN    512
struct probe_params {
    unsigned int period;
    char elf_path[MAX_PATH_LEN];
    char task_whitelist[MAX_PATH_LEN];
};
int args_parse(int argc, char **argv, char *opt_str, struct probe_params* params);

#endif
