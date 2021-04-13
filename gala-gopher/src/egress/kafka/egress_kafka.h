#ifndef __EGRESS_KAFKA_H__
#define __EGRESS_KAFKA_H__

#include <stdint.h>

#define MAX_EGRESS_KAFKA_TOPIC_LEN 128

struct egress_kafka {
    uint32_t egress_kafka_ip;
    uint16_t egress_kafka_port;
    char egress_kafka_topic[MAX_EGRESS_KAFKA_TOPIC_LEN];
};

#endif
