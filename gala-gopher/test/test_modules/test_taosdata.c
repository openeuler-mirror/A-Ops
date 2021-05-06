#include <stdint.h>
#include <CUnit/Basic.h>

#include "taosdata.h"
#include "test_taosdata.h"

#define TAOSDATA_IP     "localhost"
#define TAOSDATA_USER   "root"
#define TAOSDATA_PASS   "taosdata"
#define TAOSDATA_DB     "gala_gopher"
#define TAOSDATA_PORT   0

void TestTaosDbMgrCreate()
{
    TaosDbMgr *mgr = TaosDbMgrCreate(TAOSDATA_IP, TAOSDATA_USER, TAOSDATA_PASS, TAOSDATA_DB, TAOSDATA_PORT);

    CU_ASSERT(mgr != NULL);
    TaosDbMgrDestroy(mgr);
}

void TestTaosDataMain(CU_pSuite suite)
{
    CU_ADD_TEST(suite, TestTaosDbMgrCreate);
}

