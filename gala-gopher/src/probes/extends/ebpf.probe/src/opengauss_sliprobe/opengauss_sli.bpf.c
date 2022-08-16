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
 * Author: wo_cow
 * Create: 2022-7-29
 * Description: opengauss_sli probe bpf prog
 ******************************************************************************/
#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif

#define BPF_PROG_USER
#include "bpf.h"
#include <bpf/bpf_endian.h>
#include "opengauss_sli.h"

char g_license[] SEC("license") = "GPL";

#define BPF_F_INDEX_MASK        0xffffffffULL
#define BPF_F_CURRENT_CPU       BPF_F_INDEX_MASK

#define MAX_CONN_LEN            8192

#ifndef __PERIOD
#define __PERIOD NS(30)
#endif

enum status_t {
    STATUS_TO_READ = 0,
    STATUS_TO_WRITE = 0,
};

enum {
    PROG_SSL_READ = 0,
    PROG_SSL_WRITE,
};

struct conn_key_t {
    __u32 tgid;
    int fd;
};

struct conn_data_t {
    char req_cmd;
    char rsp_cmd;
    __u64 rtt; // rsp_ts_nsec - req_ts_nsec

    __u64 req_ts_nsec;
    __u64 last_report_ts_nsec;
    enum status_t status;
};

// ssl struct in opennssl 1.1.1
typedef long (*bio_callback_fn)();
struct ssl_method_st {};

struct bio_st {
    const struct ssl_method_st* method;
    bio_callback_fn callback;
    bio_callback_fn callback_ex;
    char* cb_arg;
    int init;
    int shutdown;
    int flags; /* extra storage */
    int retry_reason;
    int num;
};

struct ssl_st {
    int version; // protocol version
    const struct ssl_method_st *method;
    struct bio_st *rbio; // used by SSL_read
    struct bio_st *wbio; // used by SSL_write
}; // end of ssl struct in opennssl 1.1.1



struct bpf_map_def SEC("maps") conn_map = {
    .type = BPF_MAP_TYPE_HASH,
    .key_size = sizeof(struct conn_key_t),
    .value_size = sizeof(struct conn_data_t),
    .max_entries = MAX_CONN_LEN,
};

struct bpf_map_def SEC("maps") msg_event_map = {
    .type = BPF_MAP_TYPE_PERF_EVENT_ARRAY,
    .key_size = sizeof(u32),
    .value_size = sizeof(u32),
};

// Data collection args
struct bpf_map_def SEC("maps") args_map = {
    .type = BPF_MAP_TYPE_ARRAY,
    .key_size = sizeof(u32),    // const value 0
    .value_size = sizeof(struct ogsli_args_s),  // args
    .max_entries = 1,
};

static __always_inline int get_fd_from_ssl(struct ssl_st* ssl_st_p)
{
    int fd;

    if (ssl_st_p == NULL) {
        return -1;
    }

    struct bio_st *rbio_p = _(ssl_st_p->rbio);
    if (rbio_p == NULL) {
        return -1;
    }

    fd = _(rbio_p->num);
    return fd;
}

static __always_inline struct conn_data_t* get_conn_data(struct conn_key_t *conn_key)
{
    struct conn_data_t *conn_data = (struct conn_data_t *)bpf_map_lookup_elem(&conn_map, conn_key);
    return conn_data;
}

static __always_inline char read_first_byte_from_buf(const char *ori_buf, int ori_len)
{
    char msg[MAX_MSG_LEN_SSL] = {0};
    const char *buf;
    int len;

    if (ori_len < 0 || ori_buf == NULL) {
        return 0;
    }
    bpf_probe_read(&buf, sizeof(const char*), &ori_buf);
    len = ori_len < MAX_MSG_LEN_SSL ? (ori_len & (MAX_MSG_LEN_SSL - 1)) : MAX_MSG_LEN_SSL;
    bpf_probe_read_user(msg, len, buf);
    return msg[0];
}

UPROBE(SSL_read, pt_regs)
{
    UPROBE_PARMS_STASH(SSL_read, ctx, PROG_SSL_READ);
}

URETPROBE(SSL_read, pt_regs)
{
    u64 req_ts_nsec = bpf_ktime_get_ns();
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    struct probe_val val;
    const char *ori_buf;
    long err;
    char msg[MAX_MSG_LEN_SSL] = {0};
    int ori_len, len;
    struct conn_data_t *conn_data;

    if (PROBE_GET_PARMS(SSL_read, ctx, val, PROG_SSL_READ) < 0) {
        return;
    }

    ori_len = (int)PT_REGS_RC(ctx);
    if (ori_len <= 0) {
        return;
    }

    struct ssl_st* ssl_st_p = (struct ssl_st*)PROBE_PARM1(val);
    int fd = get_fd_from_ssl(ssl_st_p);
    if (fd < 0) {
        return;
    }

    struct conn_key_t conn_key = {.fd = fd, .tgid = tgid};
    conn_data = get_conn_data(&conn_key);
    if (conn_data == NULL) {
        struct conn_data_t conn_data_new = {0};
        conn_data_new.status = STATUS_TO_READ;
        err = bpf_map_update_elem(&conn_map, &conn_key, &conn_data_new, BPF_ANY);
        if (err < 0) {
            return;
        }
    }

    conn_data = get_conn_data(&conn_key);
    if (conn_data == NULL || conn_data->status != STATUS_TO_READ) {
        return;
    }

    ori_buf = (const char *)PROBE_PARM2(val);
    len = ori_len < MAX_MSG_LEN_SSL ? (ori_len & (MAX_MSG_LEN_SSL - 1)) : MAX_MSG_LEN_SSL;
    bpf_probe_read_user(msg, len, ori_buf);
    conn_data->req_ts_nsec = req_ts_nsec;
    conn_data->req_cmd = read_first_byte_from_buf((char *)PROBE_PARM2(val), (int)PROBE_PARM3(val));
    conn_data->status = STATUS_TO_WRITE;
}

static __always_inline u64 get_period()
{
    u32 key = 0;
    u64 period = __PERIOD;

    struct ogsli_args_s *args;
    args = (struct ogsli_args_s *)bpf_map_lookup_elem(&args_map, &key);
    if (args) {
        period = args->period;
    }

    return period; // units from second to nanosecond
}

static __always_inline void periodic_report(u64 ts_nsec, struct conn_data_t *conn_data,
    struct conn_key_t *conn_key, struct pt_regs *ctx)
{
    long err;
    u64 period = get_period();
    if (ts_nsec > conn_data->last_report_ts_nsec &&
        ts_nsec - conn_data->last_report_ts_nsec >= period) {
        if (conn_data->rtt < period) { // rtt larger than period is considered an invalid value
            struct msg_event_data_t msg_evt_data = {0};
            msg_evt_data.tgid = conn_key->tgid;
            msg_evt_data.fd = conn_key->fd;
            msg_evt_data.req_cmd = conn_data->req_cmd;
            msg_evt_data.rsp_cmd = conn_data->rsp_cmd;
            msg_evt_data.rtt = conn_data->rtt;
            err = bpf_perf_event_output(ctx, &msg_event_map, BPF_F_CURRENT_CPU,
                                        &msg_evt_data, sizeof(struct msg_event_data_t));
            if (err < 0) {
                bpf_printk("message event sent failed.\n");
            }
        }
        conn_data->rtt = 0;
        conn_data->last_report_ts_nsec = ts_nsec;
    }
    return;
}

UPROBE(SSL_write, pt_regs)
{
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    u64 rsp_ts_nsec = bpf_ktime_get_ns();
    struct conn_data_t *conn_data;

    struct ssl_st* ssl_st_p = (struct ssl_st*)PT_REGS_PARM1(ctx);
    int fd = get_fd_from_ssl(ssl_st_p);
    if (fd < 0) {
        return;
    }

    struct conn_key_t conn_key = {.fd = fd, .tgid = tgid};
    conn_data = get_conn_data(&conn_key);
    if (conn_data == NULL || conn_data->status != STATUS_TO_WRITE) {
        return;
    }

    conn_data->rtt = rsp_ts_nsec - conn_data->req_ts_nsec;
    conn_data->rsp_cmd = read_first_byte_from_buf((char *)PT_REGS_PARM2(ctx), (int)PT_REGS_PARM3(ctx));
    conn_data->status = STATUS_TO_READ;

    periodic_report(rsp_ts_nsec, conn_data, &conn_key, ctx);
}

UPROBE(SSL_shutdown, pt_regs)
{
    u32 tgid = bpf_get_current_pid_tgid() >> INT_LEN;
    struct conn_data_t *conn_data;

    struct ssl_st* ssl_st_p = (struct ssl_st*)PT_REGS_PARM1(ctx);
    int fd = get_fd_from_ssl(ssl_st_p);
    if (fd < 0) {
        return;
    }

    struct conn_key_t conn_key = {.fd = fd, .tgid = tgid};
    conn_data = get_conn_data(&conn_key);
    if (conn_data == NULL) {
        return;
    }

    bpf_map_delete_elem(&conn_map, &conn_key);
}
