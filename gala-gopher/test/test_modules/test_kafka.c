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
 * Author: Hubble_Zhu
 * Create: 2021-04-26
 * Description: provide gala-gopher test
 ******************************************************************************/
#include <stdint.h>
#include <CUnit/Basic.h>

#include "kafka.h"
#include "test_kafka.h"

#define KAFKA_BROKER "localhost:9092"
#define KAFKA_TOPIC "gala_gopher"

static void TestKafkaMgrCreate(void)
{
    KafkaMgr *mgr = KafkaMgrCreate(KAFKA_BROKER, KAFKA_TOPIC);

    CU_ASSERT(mgr != NULL);
    CU_ASSERT(strcmp(mgr->kafkaBroker, KAFKA_BROKER) == 0);
    CU_ASSERT(strcmp(mgr->kafkaTopic, KAFKA_TOPIC) == 0);
}

static void TestKafkaMsgProduce(void)
{
    uint32_t ret = 0;
    char msg[] = "deadbeaf";
    KafkaMgr *mgr = KafkaMgrCreate(KAFKA_BROKER, KAFKA_TOPIC);
    CU_ASSERT(mgr != NULL);

    ret = KafkaMsgProduce(mgr, msg, strlen(msg));
    CU_ASSERT(ret == 0);
}

void TestKafkaMain(CU_pSuite suite)
{
    CU_ADD_TEST(suite, TestKafkaMgrCreate);
    CU_ADD_TEST(suite, TestKafkaMsgProduce);
}

