#include <stdint.h>
#include <CUnit/Basic.h>

#include "meta.h"
#include "test_meta.h"

#define MEASUREMENT_MGR_SIZE    1024
#define META_PATH   "test_config/test.meta"

void TestMeasurementMgrCreate()
{
    MeasurementMgr *mgr = MeasurementMgrCreate(MEASUREMENT_MGR_SIZE);

    CU_ASSERT(mgr != NULL);
    CU_ASSERT(mgr->measurements != NULL);
    CU_ASSERT(mgr->measurementsNum == 0);
    CU_ASSERT(mgr->size == MEASUREMENT_MGR_SIZE);
    MeasurementMgrDestroy(mgr);
}

void TestMeasurementMgrLoad()
{
    uint32_t ret = 0;
    MeasurementMgr *mgr = MeasurementMgrCreate(MEASUREMENT_MGR_SIZE);
    CU_ASSERT(mgr != NULL);

    ret = MeasurementMgrLoad(mgr, META_PATH);
    CU_ASSERT(ret == 0);
    CU_ASSERT(mgr->measurementsNum == 1);
    CU_ASSERT(strcmp(mgr->measurements[0]->name, "test") == 0);
    CU_ASSERT(mgr->measurements[0]->fieldsNum == 8);

    MeasurementMgrDestroy(mgr);
}

void TestMetaMain(CU_pSuite suite)
{
    CU_ADD_TEST(suite, TestMeasurementMgrCreate);
    CU_ADD_TEST(suite, TestMeasurementMgrLoad);
}

