#ifndef __EGRESS__
#define __EGRESS__

#include <stdint.h>
#include <pthread.h>

#include "egress_kafka.h"
#include "egress_mongodb.h"

enum egress_mode {
    EGRESS_KAFKA = 0,
    EGRESS_MONGODB,
    EGRESS_MAX,
};

struct egress {
    enum egress_mode mode;

    union egress_cfg
    {
        /* data */
        struct egress_kafka kafka;
        struct egress_mongodb mongodb;
    } cfg;
    
    void *msg_queue;
    pthread_t tid;
};

#endif
