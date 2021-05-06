#ifndef __TEST_PROBE_H__
#define __TEST_PROBE_H__

#define TEST_SUITE_PROBE \
    {   \
        .suiteName = "TEST_PROBE",   \
        .suiteMain = TestProbeMain   \
    }

extern void TestProbeMain(CU_pSuite suite);

#endif

