/******************************************************************************
 * Copyright (c) Huawei Technologies Co., Ltd. 2021. All rights reserved.
 * iSulad licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Author: Hubble_Zhu
 * Create: 2021-04-12
 * Description:
 ******************************************************************************/
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include "kafka.h"

static void dr_msg_cb(rd_kafka_t *rk, const rd_kafka_message_t *rkmessage, void *opaque)
{
    if (rkmessage->err) {
        fprintf(stderr, "%% Message delivery failed: %s\n", rd_kafka_err2str(rkmessage->err));
    } else {
        fprintf(stderr, "%% Message delivered (%zd bytes, ""partition %"PRId32")\n",
                        rkmessage->len, rkmessage->partition);
    } /* rkmessage被librdkafka自动销毁 */
}

KafkaMgr *KafkaMgrCreate(const ConfigMgr *configMgr)
{
    rd_kafka_conf_res_t ret;
    KafkaMgr *mgr = NULL;
    char errstr[MAX_KAFKA_ERRSTR_SIZE];

    mgr = (KafkaMgr *)malloc(sizeof(KafkaMgr));
    if (mgr == NULL) {
        DEBUG("malloc memory for egress_kafka_mgr failed.\n");
        return NULL;
    }

    memset(mgr, 0, sizeof(KafkaMgr));
    memcpy(mgr->kafkaBroker, configMgr->kafkaConfig->broker, strlen(mgr->kafkaBroker));
    memcpy(mgr->kafkaTopic, configMgr->kafkaConfig->topic, strlen(mgr->kafkaTopic));
    mgr->batchNumMessages = configMgr->kafkaConfig->batchNumMessages;
    mgr->batchSize = configMgr->kafkaConfig->batchSize;
    memcpy(mgr->compressionCodec, configMgr->kafkaConfig->compressionCodec, strlen(mgr->compressionCodec));
    mgr->queueBufferingMaxKbytes = configMgr->kafkaConfig->queueBufferingMaxKbytes;
    mgr->queueBufferingMaxMessages = configMgr->kafkaConfig->queueBufferingMaxMessages;
    mgr->queueBufferingMaxMs = configMgr->kafkaConfig->queueBufferingMaxMs;

    mgr->conf = rd_kafka_conf_new();
    ret = rd_kafka_conf_set(mgr->conf, "bootstrap.servers", mgr->kafkaBroker, errstr, sizeof(errstr));
    if (ret != RD_KAFKA_CONF_OK) {
        DEBUG("set rdkafka bootstrap.servers failed.\n");
        free(mgr);
        return NULL;
    }
    rd_kafka_conf_set_dr_msg_cb(mgr->conf, dr_msg_cb);

    ret = rd_kafka_conf_set(mgr->conf, "batch.num.messages", mgr->batchNumMessages, errstr, sizeof(errstr));
    if (ret != RD_KAFKA_CONF_OK) {
        DEBUG("set rdkafka batch.num.messages failed.\n");
        free(mgr);
        return NULL;
    }
    rd_kafka_conf_set_dr_msg_cb(mgr->conf, dr_msg_cb);

    ret = rd_kafka_conf_set(mgr->conf, "batch.size", mgr->batchSize, errstr, sizeof(errstr));
    if (ret != RD_KAFKA_CONF_OK) {
        DEBUG("set rdkafka batch.size failed.\n");
        free(mgr);
        return NULL;
    }
    rd_kafka_conf_set_dr_msg_cb(mgr->conf, dr_msg_cb);

    ret = rd_kafka_conf_set(mgr->conf, "compression.codec", mgr->compressionCodec, errstr, sizeof(errstr));
    if (ret != RD_KAFKA_CONF_OK) {
        DEBUG("set rdkafka compression.codec failed.\n");
        free(mgr);
        return NULL;
    }
    rd_kafka_conf_set_dr_msg_cb(mgr->conf, dr_msg_cb);

    ret = rd_kafka_conf_set(mgr->conf, "queue.buffering.max.messages", mgr->queueBufferingMaxMessages, errstr, sizeof(errstr));
    if (ret != RD_KAFKA_CONF_OK) {
        DEBUG("set rdkafka queue.buffering.max.messages failed.\n");
        free(mgr);
        return NULL;
    }
    rd_kafka_conf_set_dr_msg_cb(mgr->conf, dr_msg_cb);

    ret = rd_kafka_conf_set(mgr->conf, "queue.buffering.max.kbytes", mgr->queueBufferingMaxKbytes, errstr, sizeof(errstr));
    if (ret != RD_KAFKA_CONF_OK) {
        DEBUG("set rdkafka queue.buffering.max.kbytes failed.\n");
        free(mgr);
        return NULL;
    }
    rd_kafka_conf_set_dr_msg_cb(mgr->conf, dr_msg_cb);

    ret = rd_kafka_conf_set(mgr->conf, "queue.buffering.max.ms", mgr->queueBufferingMaxMs, errstr, sizeof(errstr));
    if (ret != RD_KAFKA_CONF_OK) {
        DEBUG("set rdkafka queue.buffering.max.ms failed.\n");
        free(mgr);
        return NULL;
    }
    rd_kafka_conf_set_dr_msg_cb(mgr->conf, dr_msg_cb);

    mgr->rk = rd_kafka_new(RD_KAFKA_PRODUCER, mgr->conf, errstr, sizeof(errstr));
    if (mgr->rk == NULL) {
        DEBUG("failed to create new kafka_producer.\n");
        rd_kafka_conf_destroy(mgr->conf);
        free(mgr);
        return NULL;
    }

    mgr->rkt = rd_kafka_topic_new(mgr->rk, mgr->kafkaTopic,  NULL);
    if (mgr->rkt == NULL) {
        DEBUG("failed to create new kafka topic object.\n");
        rd_kafka_destroy(mgr->rk);
        rd_kafka_conf_destroy(mgr->conf);
        free(mgr);
        return NULL;
    }

    return mgr;
}

void KafkaMgrDestroy(KafkaMgr *mgr)
{
    if (mgr == NULL)
        return;

    if (mgr->rkt != NULL)
        rd_kafka_topic_destroy(mgr->rkt);

    if (mgr->rk != NULL)
        rd_kafka_destroy(mgr->rk);

    if (mgr->conf != NULL)
        rd_kafka_conf_destroy(mgr->conf);

    free(mgr);
    return;
}

int KafkaMsgProduce(const KafkaMgr *mgr, const char *msg, const uint32_t msgLen)
{
    int ret = 0;
    ret = rd_kafka_produce(mgr->rkt, RD_KAFKA_PARTITION_UA, RD_KAFKA_MSG_F_COPY, (void *)msg, msgLen, NULL, 0, NULL);
    if (ret == -1) {
        DEBUG("Failed to produce msg to topic %s: %s.\n", rd_kafka_topic_name(mgr->rkt),
                                                           rd_kafka_err2str(rd_kafka_last_error()));
        return -1;
    }
    return 0;
}

