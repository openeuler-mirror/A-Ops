#ifndef __TEST_KAFKA_H__
#define __TEST_KAKFA_H__

#define TEST_SUITE_KAFKA \
    {   \
        .suiteName = "TEST_KAFKA",   \
        .suiteMain = TestKafkaMain   \
    }

extern void TestKafkaMain(CU_pSuite suite);


#endif

