#include <stdint.h>
#include <CUnit/Basic.h>

#include "probe.h"
#include "test_probe.h"

#define PROBE_MGR_SIZE 1024

void TestProbeMgrCreate()
{
    ProbeMgr *mgr = ProbeMgrCreate(PROBE_MGR_SIZE);

    CU_ASSERT(mgr != NULL);
    CU_ASSERT(mgr->probes != NULL);
    CU_ASSERT(mgr->probesNum == 0);
    CU_ASSERT(mgr->size == PROBE_MGR_SIZE);
    ProbeMgrDestroy(mgr);
}

void TestProbeMgrPut()
{
    uint32_t ret = 0;
    ProbeMgr *mgr = ProbeMgrCreate(PROBE_MGR_SIZE);
    Probe *probe = ProbeCreate();

    CU_ASSERT(mgr != NULL);
    CU_ASSERT(probe != NULL);

    snprintf(probe->name, MAX_PROBE_NAME_LEN - 1, "test_probe");

    ret = ProbeMgrPut(mgr, probe);
    CU_ASSERT(ret == 0);
    CU_ASSERT(mgr->probesNum == 1);
    CU_ASSERT(mgr->probes[0] == probe);
    CU_ASSERT(strcmp(mgr->probes[0]->name, "test_probe") == 0);
    ProbeMgrDestroy(mgr);
}

void TestProbeMgrGet()
{
    uint32_t ret = 0;
    ProbeMgr *mgr = ProbeMgrCreate(PROBE_MGR_SIZE);
    Probe *probe = ProbeCreate();
    Probe *probe1 = NULL;

    CU_ASSERT(mgr != NULL);
    CU_ASSERT(probe != NULL);

    snprintf(probe->name, MAX_PROBE_NAME_LEN - 1, "test_probe");

    ret = ProbeMgrPut(mgr, probe);
    CU_ASSERT(ret == 0);

    probe1 = ProbeMgrGet(mgr, "test_probe");
    CU_ASSERT(probe1 != NULL);
    CU_ASSERT(probe1->fifo != NULL);
    ProbeMgrDestroy(mgr);
}

void TestProbeCreate()
{
    Probe *probe = ProbeCreate();

    CU_ASSERT(probe != NULL);
    CU_ASSERT(probe->fifo != NULL);
    ProbeDestroy(probe);
}

void TestProbeMain(CU_pSuite suite)
{
    CU_ADD_TEST(suite, TestProbeMgrCreate);
    CU_ADD_TEST(suite, TestProbeMgrPut);
    CU_ADD_TEST(suite, TestProbeMgrGet);
    CU_ADD_TEST(suite, TestProbeCreate);
}

