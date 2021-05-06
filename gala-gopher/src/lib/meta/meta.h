#ifndef __META_H__
#define __META_H__

#include <stdint.h>
#include "base.h"

typedef struct {
    char name[MAX_FIELD_NAME_LEN];
} Field;

typedef struct {
    char name[MAX_MEASUREMENT_NAME_LEN];

    uint32_t fieldsNum;
    Field fields[MAX_FIELDS_NUM];
} Measurement;

typedef struct {
    uint32_t size;
    uint32_t measurementsNum;
    Measurement **measurements;
} MeasurementMgr;

MeasurementMgr *MeasurementMgrCreate(uint32_t size);
void MeasurementMgrDestroy(MeasurementMgr *mgr);

int MeasurementMgrLoad(MeasurementMgr *mgr, const char *metaPath);

#endif

