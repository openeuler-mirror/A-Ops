#include <stdlib.h>
#include <stdint.h>
#include <CUnit/Basic.h>
#include <CUnit/Automated.h>
#include <CUnit/Console.h>

#include "test_fifo.h"
#include "test_kafka.h"
#include "test_meta.h"
#include "test_probe.h"
#include "test_taosdata.h"

typedef struct {
    char *suiteName;
    void (*suiteMain)(CU_pSuite);
} TestSuite;

TestSuite gTestSuites[] = {
    TEST_SUITE_FIFO,
    TEST_SUITE_KAFKA,
    TEST_SUITE_META,
    TEST_SUITE_PROBE,
    TEST_SUITE_TAOSDATA
};

int main(int argc, char *argv[])
{
    CU_pSuite suite;
    unsigned int num_failures;

    if (CU_initialize_registry() != CUE_SUCCESS) {
        return CU_get_error();
    }

    int suiteNum = sizeof(gTestSuites) / sizeof(gTestSuites[0]);
    for (int i = 0; i < suiteNum; i++) {
        suite = CU_add_suite(gTestSuites[i].suiteName, NULL, NULL);
        if (suite == NULL) {
            CU_cleanup_registry();
            return CU_get_error();
        }

        gTestSuites[i].suiteMain(suite);
    }

    CU_basic_set_mode(CU_BRM_VERBOSE);
    CU_basic_run_tests();

    num_failures = CU_get_number_of_failures();
    CU_cleanup_registry();
    return num_failures;
}


