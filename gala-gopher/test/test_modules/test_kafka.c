#include <stdint.h>
#include <CUnit/Basic.h>

#include "kafka.h"
#include "test_kafka.h"

#define KAFKA_BROKER "localhost:9092"
#define KAFKA_TOPIC "gala_gopher"

void TestKafkaMgrCreate()
{
    KafkaMgr *mgr = KafkaMgrCreate(KAFKA_BROKER, KAFKA_TOPIC);

    CU_ASSERT(mgr != NULL);
    CU_ASSERT(strcmp(mgr->kafkaBroker, KAFKA_BROKER) == 0);
    CU_ASSERT(strcmp(mgr->kafkaTopic, KAFKA_TOPIC) == 0);
    // KafkaMgrDestroy(mgr);
}

void TestKafkaMsgProduce()
{
    uint32_t ret = 0;
    char msg[] = "deadbeaf";
    KafkaMgr *mgr = KafkaMgrCreate(KAFKA_BROKER, KAFKA_TOPIC);
    CU_ASSERT(mgr != NULL);

    ret = KafkaMsgProduce(mgr, msg, strlen(msg));
    CU_ASSERT(ret == 0);
    // KafkaMgrDestroy(mgr);
}

void TestKafkaMain(CU_pSuite suite)
{
    CU_ADD_TEST(suite, TestKafkaMgrCreate);
    CU_ADD_TEST(suite, TestKafkaMsgProduce);
}

