#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include "kafka.h"

static void dr_msg_cb(rd_kafka_t *rk, const rd_kafka_message_t *rkmessage, void *opaque){
    if(rkmessage->err) {
        fprintf(stderr, "%% Message delivery failed: %s\n", rd_kafka_err2str(rkmessage->err));
    } else {
        fprintf(stderr, "%% Message delivered (%zd bytes, ""partition %"PRId32")\n",
                        rkmessage->len, rkmessage->partition);
    } /* rkmessage被librdkafka自动销毁*/
}

KafkaMgr *KafkaMgrCreate(const char *broker, const char *topic)
{
    rd_kafka_conf_res_t ret;
    KafkaMgr *mgr = NULL;
    char errstr[MAX_KAFKA_ERRSTR_SIZE];
    
    mgr = (KafkaMgr *)malloc(sizeof(KafkaMgr));
    if (mgr == NULL) {
        printf("malloc memory for egress_kafka_mgr failed.\n");
        return NULL;
    }

    memset(mgr, 0, sizeof(KafkaMgr));
    memcpy(mgr->kafkaBroker, broker, strlen(broker));
    memcpy(mgr->kafkaTopic, topic, strlen(topic));

    mgr->conf = rd_kafka_conf_new();
    ret = rd_kafka_conf_set(mgr->conf, "bootstrap.servers", mgr->kafkaBroker, errstr, sizeof(errstr));
    if (ret != RD_KAFKA_CONF_OK) {
        printf("set rdkafka bootstrap.servers failed.\n");
        free(mgr);
        return NULL;
    }
    rd_kafka_conf_set_dr_msg_cb(mgr->conf, dr_msg_cb);

    mgr->rk = rd_kafka_new(RD_KAFKA_PRODUCER, mgr->conf, errstr, sizeof(errstr));
    if (mgr->rk == NULL) {
        printf("failed to create new kafka_producer.\n");
        rd_kafka_conf_destroy(mgr->conf);
        free(mgr);
        return NULL;
    }

    mgr->rkt = rd_kafka_topic_new(mgr->rk, mgr->kafkaTopic,  NULL);
    if (mgr->rkt == NULL) {
        printf("failed to create new kafka topic object.\n");
        rd_kafka_destroy(mgr->rk);
        rd_kafka_conf_destroy(mgr->conf);
        free(mgr);
        return NULL;    
    }

    return mgr;

}

void KafkaMgrDestroy(KafkaMgr *mgr)
{
    if (mgr == NULL) {
        return;
    }

    if (mgr->rkt != NULL) {
        rd_kafka_topic_destroy(mgr->rkt);
    }
    if (mgr->rk != NULL) {
        rd_kafka_destroy(mgr->rk);
    }
    if (mgr->conf != NULL) {
        rd_kafka_conf_destroy(mgr->conf);
    }

    free(mgr);
    return;

}

int KafkaMsgProduce(KafkaMgr *mgr, const char *msg, const uint32_t msgLen)
{
    int ret = 0;
    ret = rd_kafka_produce(mgr->rkt, RD_KAFKA_PARTITION_UA, RD_KAFKA_MSG_F_COPY, (void *)msg, msgLen, NULL, 0, NULL);
    if (ret == -1)
    {
        printf("Failed to produce msg to topic %s: %s.\n", rd_kafka_topic_name(mgr->rkt), 
                                                           rd_kafka_err2str(rd_kafka_last_error()));
        return -1;
    }
    return 0;
}


