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
 * Create: 2022-02-22
 * Description: block probe
 ******************************************************************************/
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/resource.h>

#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif

#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif

#include "bpf.h"
#include "args.h"
#include "blockprobe.skel.h"
#include "blockprobe_iscsi.skel.h"
#include "blockprobe_iscsi_tp.skel.h"
#include "blockprobe_iscsi_sas.skel.h"
#include "blockprobe.h"
#include "event.h"

#define OO_NAME "block"  // Observation Object name
#define ISCSI_MOD "libiscsi"
#define ISCSI_SAS_MOD "libsas"
#define ISCSI_TP_MOD "scsi_transport_iscsi"
#define BLOCK_MAP_PATH "/sys/fs/bpf/probe/block_map"
#define SCSI_BLOCK_MAP_PATH "/sys/fs/bpf/probe/scsi_block_map"

#define RM_BLOCK_MAP_PATH "/usr/bin/rm -rf /sys/fs/bpf/probe/block_map"
#define RM_SCSI_MAP_PATH "/usr/bin/rm -rf /sys/fs/bpf/probe/scsi_block_map"

#define IS_LOWERCASE_LEETER(a) (((a) >= 'a') && ((a) <= 'z'))

#define SPLIT_SYMBOL "|"
#define COLON_SYMBOL ':'
#define LSBLK_LIST_CMD "lsblk -l | awk 'NR > 1 {print $1 \"|\" $2 \"|\" $6}'"
#define LSBLK_TREE_CMD "lsblk -t | awk 'NR > 1 {print $1}'"

static const char *const blk_type_str[] = {
        [BLK_TYPE_INVALID] = "null",
        [BLK_TYPE_DISK] = "disk",
        [BLK_TYPE_PART] = "part",
        [BLK_TYPE_LVM] = "lvm",
};

#define __IS_SCSI_BLOCK(name) (name[0] == 's' && name[1] == 'd')

#define __LOAD_PROBE(probe_name, end, load) \
    OPEN(probe_name, end, load); \
    MAP_SET_PIN_PATH(probe_name, block_map, BLOCK_MAP_PATH, load); \
    MAP_SET_PIN_PATH(probe_name, scsi_block_map, SCSI_BLOCK_MAP_PATH, load); \
    LOAD_ATTACH(probe_name, end, load)

static volatile sig_atomic_t g_stop;
static struct probe_params params = {.period = DEFAULT_PERIOD};
static int block_map_fd, scsi_block_map_fd;

static void sig_int(int signo)
{
    g_stop = 1;
}

static char __is_exist_mod(const char *mod)
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

static char is_exist_iscsi_mod()
{
    return __is_exist_mod(ISCSI_MOD);
}

static char is_exist_iscsi_sas_mod()
{
    return __is_exist_mod(ISCSI_SAS_MOD);
}

static char is_exist_iscsi_tp_mod()
{
    return __is_exist_mod(ISCSI_TP_MOD);
}

static inline int create_scsi_block(struct block_key *bkey)
{
    __u32 flag = 0;
    DEBUG("[BLOCKPROB] upd scsi block entry [%d:%d]).\n", bkey->major, bkey->first_minor);
    return bpf_map_update_elem(scsi_block_map_fd, &flag, bkey, BPF_ANY);
}

static inline int __upd_blk_entry(struct block_key *bkey, struct block_data *bdata)
{
    DEBUG("[BLOCKPROB] upd blk entry(%s[disk %s type %s] [%d:%d]).\n", bdata->blk_name, bdata->disk_name,
            blk_type_str[bdata->blk_type], bkey->major, bkey->first_minor);
    return bpf_map_update_elem(block_map_fd, bkey, bdata, BPF_ANY);
}

static char* __get_blk_name(char *buf)
{
    char *p;
    size_t pos;
    size_t len = strlen(buf);
    if (len == 0)
        return NULL;

    pos = 0;
    p = buf + pos;
    while ((pos < len) && (!IS_LOWERCASE_LEETER(*p))) {
        pos++;
        p = buf + pos;
    }
    
    if (pos >= len)
        return NULL;

    return p;
}

static void __do_get_disk_name(const char* blk_name, char *disk, size_t len)
{
    FILE *f = NULL;
    char cmd[COMMAND_LEN];
    char line[LINE_BUF_LEN];
    char *p;
    char disk_name[DISK_NAME_LEN];

    cmd[0] = 0;
    (void)strncpy(cmd, LSBLK_TREE_CMD, COMMAND_LEN);
    f = popen(cmd, "r");
    if (f == NULL) {
        return;
    }
    while (!feof(f)) {
        line[0] = 0;
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            break;
        }
        SPLIT_NEWLINE_SYMBOL(line);
        p = __get_blk_name(line);
        if (p && (p == line)) {
            // record last disk name
            disk_name[0] = 0;
            (void)strncpy(disk_name, p, DISK_NAME_LEN);
        }

        if (p && (p != line) && (strcmp(blk_name, p) == 0)) {
            (void)strncpy(disk, disk_name, len);
            break;
        }
    }

    pclose(f);
    return;
}

static inline void __get_maj_and_min(char *buf, int *major, int *minor)
{
    char maj_s[INT_LEN];
    char min_s[INT_LEN];
    size_t s = strlen(buf);
    char *p = buf, *p2 = buf + s;

    while (*p != COLON_SYMBOL && p < (buf + s)) {
        p++;
    }
        
    if (p >= p2 || p <= buf || (int)(p2 - p - 1) <= 0)
        return;

    (void)memset(maj_s, 0, INT_LEN);
    (void)memcpy(maj_s, buf, p - buf);
    *major = atoi(maj_s);

    (void)memset(min_s, 0, INT_LEN);
    (void)memcpy(min_s, p + 1, p2 - p - 1);
    *minor = atoi(min_s);
}

static inline void __get_blk_type(const char *buf, enum blk_type_e *blk_type)
{
    if (strcmp(buf, blk_type_str[BLK_TYPE_DISK]) == 0) {
        *blk_type = BLK_TYPE_DISK;
    } else if (strcmp(buf, blk_type_str[BLK_TYPE_PART]) == 0) {
        *blk_type = BLK_TYPE_PART;
    } else if (strcmp(buf, blk_type_str[BLK_TYPE_LVM]) == 0) {
        *blk_type = BLK_TYPE_LVM;
    } else {
        *blk_type = BLK_TYPE_INVALID;
    }
}

static void __do_load_one_blk(char *buf)
{
    char *p;
    struct block_key bkey = {0};
    struct block_data bdata = {0};
    char maj_minor_s[LINE_BUF_LEN];
    
    p = strtok(buf, SPLIT_SYMBOL);
    while (p) {
        if (bdata.blk_name[0] == 0) {
           (void)strncpy(bdata.blk_name, p, DISK_NAME_LEN);
           p = strtok(NULL, SPLIT_SYMBOL);
           continue;
        }

        if ((bkey.major == 0) && (bkey.first_minor == 0)) {
            maj_minor_s[0] = 0;
            (void)strncpy(maj_minor_s, p, LINE_BUF_LEN);
            __get_maj_and_min(maj_minor_s, &(bkey.major), &(bkey.first_minor));
            p = strtok(NULL, SPLIT_SYMBOL);
            continue;
        }

        if (bdata.blk_type == BLK_TYPE_INVALID) {
            __get_blk_type((const char *)p, &bdata.blk_type);
        }

        if (bdata.blk_type == BLK_TYPE_DISK) {
            (void)strncpy(bdata.disk_name, bdata.blk_name, DISK_NAME_LEN);
        }

        p = strtok(NULL, SPLIT_SYMBOL);
    }

    if (bdata.blk_type != BLK_TYPE_INVALID) {
        if (bdata.blk_type != BLK_TYPE_DISK) {
            __do_get_disk_name((const char*)bdata.blk_name, bdata.disk_name, DISK_NAME_LEN);
        }
        (void)__upd_blk_entry(&bkey, &bdata);
        if ((bdata.blk_type == BLK_TYPE_DISK) && __IS_SCSI_BLOCK(bdata.blk_name)) {
            (void)create_scsi_block(&bkey);
        }
    }
}

/**
lsblk -l | awk 'NR > 1 {print $1 "|" $2 "|" $6}'
sda|8:0|disk
sda1|8:1|part
sda2|8:2|part
sr0|11:0|rom
*/
static void do_load_blk()
{
    FILE *f = NULL;
    char cmd[COMMAND_LEN];
    char line[LINE_BUF_LEN];

    cmd[0] = 0;
    (void)strncpy(cmd, LSBLK_LIST_CMD, COMMAND_LEN);
    f = popen(cmd, "r");
    if (f == NULL) {
        return;
    }
    while (!feof(f)) {
        line[0] = 0;
        if (fgets(line, LINE_BUF_LEN, f) == NULL) {
            break;
        }
        SPLIT_NEWLINE_SYMBOL(line);
        __do_load_one_blk(line);
    }

    pclose(f);
    return;
}

#define __ENTITY_ID_LEN 32
static void build_entity_id(struct block_key *key, char *buf, int buf_len)
{
    (void)snprintf(buf, buf_len, "%d_%d",
                        key->major,
                        key->first_minor);
}

static void report_block(struct block_key *key, struct block_data *bdata)
{
    char entityId[__ENTITY_ID_LEN];
    unsigned int latency_thr_us;
    unsigned int jitter_thr_us;
    struct latency_stats* flush_stats = &(bdata->blk_stats.flush);
    struct latency_stats* request_stats = &(bdata->blk_stats.req);
    struct iscsi_err_stats* iscsi_err = &(bdata->iscsi_err_stats);

    if (params.logs == 0)
        return;

    entityId[0] = 0;
    build_entity_id(key, entityId, __ENTITY_ID_LEN);

    latency_thr_us = params.latency_thr << 3; // milliseconds to microseconds
    jitter_thr_us = params.jitter_thr << 3; // milliseconds to microseconds

    if (iscsi_err->count_iscsi_err != 0) {
        report_logs(OO_NAME,
                    entityId,
                    "count_iscsi_err",
                    EVT_SEC_WARN,
                    "Iscsi errors(%llu) occured on Block(%s, disk %s).",
                    iscsi_err->count_iscsi_err,
                    bdata->blk_name,
                    bdata->disk_name);
    }

    if (iscsi_err->count_iscsi_tmout != 0) {
        report_logs(OO_NAME,
                    entityId,
                    "count_iscsi_tmout",
                    EVT_SEC_WARN,
                    "Iscsi timeout(%llu) occured on Block(%s, disk %s).",
                    iscsi_err->count_iscsi_tmout,
                    bdata->blk_name,
                    bdata->disk_name);
    }

    if ((jitter_thr_us > 0) && (flush_stats->latency_jitter > jitter_thr_us)) {
        report_logs(OO_NAME,
                    entityId,
                    "latency_flush_jitter",
                    EVT_SEC_WARN,
                    "Jitter latency of flush operation(%llu) exceeded threshold, occured on Block(%s, disk %s).",
                    flush_stats->latency_jitter,
                    bdata->blk_name,
                    bdata->disk_name);
    }

    if ((latency_thr_us > 0) && (flush_stats->latency_max > latency_thr_us)) {
        report_logs(OO_NAME,
                    entityId,
                    "latency_flush_max",
                    EVT_SEC_WARN,
                    "Latency of flush operation(%llu) exceeded threshold, occured on Block(%s, disk %s).",
                    flush_stats->latency_max,
                    bdata->blk_name,
                    bdata->disk_name);
    }

    if ((jitter_thr_us > 0) && (request_stats->latency_jitter > jitter_thr_us)) {
        report_logs(OO_NAME,
                    entityId,
                    "latency_req_jitter",
                    EVT_SEC_WARN,
                    "Jitter latency of request operation(%llu) exceeded threshold, occured on Block(%s, disk %s).",
                    request_stats->latency_jitter,
                    bdata->blk_name,
                    bdata->disk_name);
    }

    if ((latency_thr_us > 0) && (request_stats->latency_max > latency_thr_us)) {
        report_logs(OO_NAME,
                    entityId,
                    "latency_req_max",
                    EVT_SEC_WARN,
                    "Latency of request operation(%llu) exceeded threshold, occured on Block(%s, disk %s).",
                    request_stats->latency_max,
                    bdata->blk_name,
                    bdata->disk_name);
    }
}

static void pull_block_stats(int map_fd)
{
    int ret;
    struct block_key ckey = {0};
    struct block_key nkey = {0};
    struct block_data data;

    while (bpf_map_get_next_key(map_fd, &ckey, &nkey) != -1) {
        ret = bpf_map_lookup_elem(map_fd, &nkey, &data);
        if (ret != 0) {
            ckey = nkey;
            continue;
        }

        report_block(&nkey, &data);

        fprintf(stdout, "|%s|%d|%d|%s|%s|%s|%llu|%llu|%llu|%llu|%u|%llu|%llu|%llu"
                "|%llu|%u|%llu|%llu|%llu|%llu|%u|%llu|%llu|%llu|%llu|%u|%llu|%llu|%llu|%llu|%llu|%llu|%llu|\n",
                OO_NAME,
                nkey.major,
                nkey.first_minor,
                blk_type_str[data.blk_type],
                data.blk_name,
                data.disk_name,
                data.blk_stats.req.latency_max,
                data.blk_stats.req.latency_last,
                data.blk_stats.req.latency_sum,
                data.blk_stats.req.latency_jitter,
                data.blk_stats.req.count_latency,
                data.blk_stats.flush.latency_max,
                data.blk_stats.flush.latency_last,
                data.blk_stats.flush.latency_sum,
                data.blk_stats.flush.latency_jitter,
                data.blk_stats.flush.count_latency,
                data.blk_drv_stats.latency_max,
                data.blk_drv_stats.latency_last,
                data.blk_drv_stats.latency_sum,
                data.blk_drv_stats.latency_jitter,
                data.blk_drv_stats.count_latency,
                data.blk_dev_stats.latency_max,
                data.blk_dev_stats.latency_last,
                data.blk_dev_stats.latency_sum,
                data.blk_dev_stats.latency_jitter,
                data.blk_dev_stats.count_latency,
                data.iscsi_err_stats.count_iscsi_tmout,
                data.iscsi_err_stats.count_iscsi_err,
                data.conn_stats.conn_err[ISCSI_ERR_BAD_OPCODE],
                data.conn_stats.conn_err[ISCSI_ERR_XMIT_FAILED],
                data.conn_stats.conn_err[ISCSI_ERR_NOP_TIMEDOUT],
                data.conn_stats.conn_err[ISCSI_ERR_CONN_FAILED],
                data.sas_stats.count_sas_abort);

        DEBUG("[%s] MAJ[%d] MIN[%d] blk_t[%s] blk[%s] disk[%s] req_m[%llu] req_l[%llu] req_s[%llu] req_j[%llu] req_c[%u] "
                "flush_m[%llu] flush_l[%llu] flush_s[%llu] flush_j[%llu] flush_c[%u] "
                "drv_m[%llu] drv_l[%llu] drv_s[%llu] drv_j[%llu] drv_c[%u] "
                "dev_m[%llu] dev_l[%llu] dev_s[%llu] dev_j[%llu] dev_c[%u] "
                "scsi_tm[%llu] scsi_err[%llu] bad_op[%llu] xmit_f[%llu] conn_tm[%llu] conn_f[%llu] sas_abort[%llu]\n",
                OO_NAME,
                nkey.major,
                nkey.first_minor,
                blk_type_str[data.blk_type],
                data.blk_name,
                data.disk_name,
                data.blk_stats.req.latency_max,
                data.blk_stats.req.latency_last,
                data.blk_stats.req.latency_sum,
                data.blk_stats.req.latency_jitter,
                data.blk_stats.req.count_latency,
                data.blk_stats.flush.latency_max,
                data.blk_stats.flush.latency_last,
                data.blk_stats.flush.latency_sum,
                data.blk_stats.flush.latency_jitter,
                data.blk_stats.flush.count_latency,
                data.blk_drv_stats.latency_max,
                data.blk_drv_stats.latency_last,
                data.blk_drv_stats.latency_sum,
                data.blk_drv_stats.latency_jitter,
                data.blk_drv_stats.count_latency,
                data.blk_dev_stats.latency_max,
                data.blk_dev_stats.latency_last,
                data.blk_dev_stats.latency_sum,
                data.blk_dev_stats.latency_jitter,
                data.blk_dev_stats.count_latency,
                data.iscsi_err_stats.count_iscsi_tmout,
                data.iscsi_err_stats.count_iscsi_err,
                data.conn_stats.conn_err[ISCSI_ERR_BAD_OPCODE],
                data.conn_stats.conn_err[ISCSI_ERR_XMIT_FAILED],
                data.conn_stats.conn_err[ISCSI_ERR_NOP_TIMEDOUT],
                data.conn_stats.conn_err[ISCSI_ERR_CONN_FAILED],
                data.sas_stats.count_sas_abort);

        ckey = nkey;
    }

    return;
}
int main(int argc, char **argv)
{
    int err = -1;
    char iscsi, iscsi_tp, iscsi_sas;
    FILE *fp = NULL;
    
    err = args_parse(argc, argv, &params);
    if (err != 0)
        return -1;

    printf("arg parse interval time:%us\n", params.period);
    fp = popen(RM_BLOCK_MAP_PATH, "r");
    if (fp != NULL) {
        (void)pclose(fp);
        fp = NULL;
    }
    fp = popen(RM_SCSI_MAP_PATH, "r");
    if (fp != NULL) {
        (void)pclose(fp);
    }

    iscsi = is_exist_iscsi_mod();
    iscsi_tp = is_exist_iscsi_tp_mod();
    iscsi_sas = is_exist_iscsi_sas_mod();

    INIT_BPF_APP(blockprobe, EBPF_RLIM_LIMITED);
    
    __LOAD_PROBE(blockprobe, err4, 1);
    __LOAD_PROBE(blockprobe_iscsi, err3, iscsi);
    __LOAD_PROBE(blockprobe_iscsi_tp, err2, iscsi_tp);
    __LOAD_PROBE(blockprobe_iscsi_sas, err, iscsi_sas);

    block_map_fd = GET_MAP_FD(blockprobe, block_map);
    scsi_block_map_fd = GET_MAP_FD(blockprobe, scsi_block_map);

    do_load_blk();

    if (signal(SIGINT, sig_int) == SIG_ERR) {
        fprintf(stderr, "can't set signal handler: %s\n", strerror(errno));
        goto err;
    }

    printf("Successfully started!\n");

    while (g_stop == 0) {
        pull_block_stats(block_map_fd);
        sleep(params.period);
    }

err:
    if (iscsi_sas) {
        UNLOAD(blockprobe_iscsi_sas);
    }
err2:
    if (iscsi_tp) {
        UNLOAD(blockprobe_iscsi_tp);
    }
err3:
    if (iscsi) {
        UNLOAD(blockprobe_iscsi);
    }
err4:
    UNLOAD(blockprobe);
    return -err;
}
