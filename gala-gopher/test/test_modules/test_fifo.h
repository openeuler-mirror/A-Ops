#ifndef __TEST_FIFO_H__
#define __TEST_FIFO_H__

#define TEST_SUITE_FIFO \
    {   \
        .suiteName = "TEST_FIFO",   \
        .suiteMain = TestFifoMain   \
    }

extern void TestFifoMain(CU_pSuite suite);

#endif

