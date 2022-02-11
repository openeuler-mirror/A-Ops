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
 * Create: 2021-09-28
 * Description: bpf header
 ******************************************************************************/
#ifndef __GOPHER_BPF_H__
#define __GOPHER_BPF_H__

#define __PROBE_MATCH_MAP_PIN_PATH "/sys/fs/bpf/probe/match_map"
#define INT_LEN    32
#define THOUSAND   1000
#define PATH_NUM   20

#ifndef GOPHER_DEBUG
#define DEBUG
#else
#define DEBUG printf
#endif

#include "__share_map_match.h"
#include "__bpf_kern.h"
#include "__bpf_usr.h"
#include "__libbpf.h"

#endif
