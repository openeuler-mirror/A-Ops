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
 * Author: luzhihao
 * Create: 2022-03-4
 * Description: 
 ******************************************************************************/
#ifndef __TCPLINK__H
#define __TCPLINK__H

#include <time.h>

struct metric_key {
    struct ip c_ip;
    struct ip s_ip;
    __u16 s_port;
    __u16 proto;
    __u32 tgid;     // process id
};

struct metric_data {
    char comm[TASK_COMM_LEN];
    __u32 link_num;
    __u64 rx;
    __u64 tx;
    __u32 segs_in;
    __u32 segs_out;
    __u32 total_retrans;
    __u32 lost;
    __u32 srtt;
    __u32 srtt_max;
    __u32 rcv_wnd_min;
    __u32 rcv_wnd_avg;
    __u32 rcv_wnd_max;
    __u32 backlog_drops;
    __u32 sk_drops;
    __u32 md5_hash_drops;
    __u32 filter_drops;
    __u32 ofo_count;
    __u32 tmout;
    __u32 rcvque_full;
    __u32 sndbuf_limit;
    __u32 send_rsts;
    __u32 receive_rsts;
    char role;
    time_t last_active_tm;
};


#endif
