#ifndef __TEST_META_H__
#define __TEST_META_H__

#define TEST_SUITE_META \
    {   \
        .suiteName = "TEST_META",   \
        .suiteMain = TestMetaMain   \
    }

extern void TestMetaMain(CU_pSuite suite);

#endif

