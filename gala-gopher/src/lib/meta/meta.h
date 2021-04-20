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

Measurement *MeasurementCreate();
void MeasurementDestroy(Measurement *mm);

MeasurementMgr *MeasurementMgrCreate(uint32_t size);
void MeasurementMgrDestroy(MeasurementMgr *mgr);

int MeasurementMgrAdd(MeasurementMgr *mgr, Measurement *measurement);
Measurement *MeasurementMgrGet(MeasurementMgr *mgr, const char *name);

int MeasurementMgrLoad(MeasurementMgr *mgr, const char *metaPath);

#endif

