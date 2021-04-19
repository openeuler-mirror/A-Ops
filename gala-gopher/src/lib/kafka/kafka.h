#ifndef __KAFKA_H__
#define __KAFKA_H__


#include <stdint.h>
#include <rdkafka.h>

#define MAX_KAFKA_BROKER_LEN 128
#define MAX_KAFKA_TOPIC_LEN  128

typedef struct {
    char kafkaBroker[MAX_KAFKA_BROKER_LEN];
    char kafkaTopic[MAX_KAFKA_TOPIC_LEN];
    
    rd_kafka_t *rk;
    rd_kafka_topic_t *rkt;
    rd_kafka_conf_t *conf;
} KafkaMgr;


KafkaMgr *KafkaMgrCreate(const char *broker, const char *topic);
void KafkaMgrDestroy(KafkaMgr *mgr);

int KafkaMsgProduce(KafkaMgr *mgr, const char *msg, const uint32_t msgLen);

#endif

