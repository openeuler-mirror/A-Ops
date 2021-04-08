#ifndef __RAMDB__
#define __RAMDB__
#include <stdint.h>

#define MAX_MEASUREMENT_NUM 64
#define MAX_MEASUREMENT_NAME_LEN 128
#define MAX_MEASUREMENT_FIELD_NUM 64
#define MAX_FILED_NAME_LEN 128
#define MAX_FILED_VALUE_LEN 128

struct ramdb_field {
    char name[MAX_FILED_NAME_LEN];
    char value[MAX_FILED_VALUE_LEN];
};

struct ramdb_measurement {
    char name[MAX_MEASUREMENT_NAME_LEN];
    struct db_field fields[MAX_MEASUREMENT_FIELD_NUM];
};

struct ramdb {
    uint32_t measurements_num;
    struct db_measurement measurements[MAX_MEASUREMENT_NUM];
};

struct ramdb *create_ramdb_mgr();
void destroy_ramdb_mgr(struct ramdb *ramdb_mgr);

#endif
