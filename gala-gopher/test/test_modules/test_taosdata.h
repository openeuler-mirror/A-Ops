#ifndef __TEST_TAOSDATA_H__
#define __TEST_TAOSDATA_H__

#define TEST_SUITE_TAOSDATA \
    {   \
        .suiteName = "TEST_TAOSDATA",   \
        .suiteMain = TestTaosDataMain   \
    }

extern void TestTaosDataMain(CU_pSuite suite);

#endif

