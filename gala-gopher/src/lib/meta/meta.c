#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include <libconfig.h>
#include "meta.h"

Measurement *MeasurementCreate()
{
    Measurement *mm = NULL;
    mm = (Measurement *)malloc(sizeof(Measurement));
    if (mm == NULL) {
        return NULL;
    }

    memset(mm, 0, sizeof(Measurement));
    return mm;
}

void MeasurementDestroy(Measurement *mm)
{
    if (mm == NULL) {
        return;
    }
    free(mm);
    return;
}

MeasurementMgr *MeasurementMgrCreate(uint32_t size)
{
    MeasurementMgr *mgr = NULL;
    mgr = (MeasurementMgr *)malloc(sizeof(MeasurementMgr));
    if (mgr == NULL) {
        return NULL;
    }
    memset(mgr, 0, sizeof(MeasurementMgr));

    mgr->measurements = (Measurement **)malloc(sizeof(Measurement *) * size);
    if (mgr->measurements == NULL) {
        free(mgr);
        return NULL;
    }
    memset(mgr->measurements, 0, sizeof(Measurement *) * size);
    mgr->size = size;

    return mgr;
}

void MeasurementMgrDestroy(MeasurementMgr *mgr)
{
    if (mgr == NULL) {
        return;
    }

    for (int i = 0; i < mgr->measurementsNum; i++) {
        if (mgr->measurements[i] != NULL) {
            MeasurementDestroy(mgr->measurements[i]);
        }
    }

    free(mgr->measurements);
    free(mgr);
    return;
}

int MeasurementMgrAdd(MeasurementMgr *mgr, Measurement *measurement)
{
    Measurement *mm = NULL;
    mm = MeasurementMgrGet(mgr, measurement->name);
    if (mm != NULL) {
        return -1;
    }

    if (mgr->measurementsNum == mgr->size) {
        return -1;
    }
    mgr->measurements[mgr->measurementsNum] = measurement;
    mgr->measurementsNum++;
    return 0;
}

Measurement *MeasurementMgrGet(MeasurementMgr *mgr, const char *name)
{
    for (int i = 0; i < mgr->measurementsNum; i++) {
        if (strcmp(mgr->measurements[i]->name, name) == 0) {
            return mgr->measurements[i];
        }
    }

    return NULL;
}

static int MeasurementLoad(Measurement *mm, config_setting_t *mmConfig)
{
    int ret = 0;
    const char *name;
    const char *field;
    ret = config_setting_lookup_string(mmConfig, "name", &name);
    if (ret == 0) {
        printf("load measurement name failed.\n");
        return -1;
    }

    memcpy(mm->name, name, strlen(name));
    config_setting_t *fields = config_setting_lookup(mmConfig, "fields");
    int field_count = config_setting_length(fields);
    if (field_count > MAX_FIELDS_NUM_PER_MEASUREMENT) {
        printf("Too many fields.\n");
        return -1;
    }

    for (int j = 0; j < field_count; j++) {
        field = config_setting_get_string_elem(fields, j);
        if (field == NULL) {
            printf("load measurement field failed.\n");
            return -1;
        }

        memcpy(mm->fields[j].name, field, strlen(field));
        mm->fieldsNum++;
    }

    return 0;
}

int MeasurementMgrLoad(MeasurementMgr *mgr, const char *metaPath)
{
    int ret = 0;
    config_t cfg;
    config_setting_t *measurements;

    char *name;
    char *field;

    config_init(&cfg);
    ret = config_read_file(&cfg, metaPath);
    if (ret == 0) {
        printf("config read file %s failed.\n", metaPath);
        config_destroy(&cfg);
        return -1;
    }

    measurements = config_lookup(&cfg, "measurements");
    if (measurements == NULL) {
        printf("get measurements failed.\n");
        config_destroy(&cfg);
        return -1;
    }

    int count = config_setting_length(measurements);
    for (int i = 0; i < count; i++) {
        config_setting_t *measurement = config_setting_get_elem(measurements, i);
        
        Measurement *mm = MeasurementCreate();
        if (mm == NULL) {
            printf("malloc measurement failed.\n");
            config_destroy(&cfg);
            return -1;
        }
        
        ret = MeasurementLoad(mm, measurement);
        if (ret != 0) {
            printf("load_measurement failed.\n");
            config_destroy(&cfg);
            return -1;
        }

        ret = MeasurementMgrAdd(mgr, mm);
        if (ret != 0) {
            printf("Add measurements failed.\n");
            config_destroy(&cfg);
            return -1;
        }
    }

    config_destroy(&cfg);
    return 0;    
}