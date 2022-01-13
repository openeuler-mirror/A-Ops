#include <stdlib.h>
#include <stdint.h>
#include <CUnit/Basic.h>
#include <CUnit/Automated.h>
#include <CUnit/Console.h>

#include "test_probes.h"

int main(int argc, char *argv[])
{
    CU_pSuite suite;
    unsigned int num_failures;

    if (CU_initialize_registry() != CUE_SUCCESS) {
        return CU_get_error();
    }

    suite = CU_add_suite("test_probes", NULL, NULL);
    if (suite == NULL) {
        CU_cleanup_registry();
        return CU_get_error();
    }

    CU_ADD_TEST(suite, test_probe_meta_coinstance);

    CU_basic_set_mode(CU_BRM_VERBOSE);
    CU_basic_run_tests();

    num_failures = CU_get_number_of_failures();
    CU_cleanup_registry();
    return num_failures;
}

