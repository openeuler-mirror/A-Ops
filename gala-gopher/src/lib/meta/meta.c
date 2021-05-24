#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>

#include <libconfig.h>
#include "meta.h"

#if GALA_GOPHER_INFO("inner func")
Measurement *MeasurementCreate();
void MeasurementDestroy(Measurement *mm);
int MeasurementMgrAdd(MeasurementMgr *mgr, Measurement *measurement);
Measurement *MeasurementMgrGet(MeasurementMgr *mgr, const char *name);
#endif

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

static int FieldLoad(Field *field, config_setting_t *fieldConfig)
{
    int ret = 0;
    const char *token;

    memset(field, 0, sizeof(Field));
    ret = config_setting_lookup_string(fieldConfig, "description", &token);
    if (ret == 0) {
        printf("load field description failed.\n");
        return -1;
    }
    memcpy(field->description, token, strlen(token));

    ret = config_setting_lookup_string(fieldConfig, "type", &token);
    if (ret == 0) {
        printf("load field type failed.\n");
        return -1;
    }
    memcpy(field->type, token, strlen(token));

    ret = config_setting_lookup_string(fieldConfig, "name", &token);
    if (ret == 0) {
        printf("load field name failed.\n");
        return -1;
    }
    memcpy(field->name, token, strlen(token));

    return 0;
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
    int fieldsCount = config_setting_length(fields);
    if (fieldsCount > MAX_FIELDS_NUM) {
        printf("Too many fields.\n");
        return -1;
    }

    for (int i = 0; i < fieldsCount; i++) {
        config_setting_t *fieldConfig = config_setting_get_elem(fields, i);

        ret = FieldLoad(&mm->fields[i], fieldConfig);
        if (ret != 0) {
            printf("[META] load measurement field failed.\n");
        }

        mm->fieldsNum++;
    }

    return 0;
}

static int MeasurementMgrLoadSingleMeta(MeasurementMgr *mgr, const char *metaPath)
{
    int ret = 0;
    config_t cfg;
    config_setting_t *measurements = NULL;

    char *name = NULL;
    char *field = NULL;

    printf("[META] begin load meta: %s.\n", metaPath);

    config_init(&cfg);
    ret = config_read_file(&cfg, metaPath);
    if (ret == 0) {
        printf("[META] config read file %s failed.\n", metaPath);
        config_destroy(&cfg);
        return -1;
    }

    measurements = config_lookup(&cfg, "measurements");
    if (measurements == NULL) {
        printf("[META] get measurements failed.\n");
        config_destroy(&cfg);
        return -1;
    }

    int count = config_setting_length(measurements);
    for (int i = 0; i < count; i++) {
        config_setting_t *measurement = config_setting_get_elem(measurements, i);

        Measurement *mm = MeasurementCreate();
        if (mm == NULL) {
            printf("[META] malloc measurement failed.\n");
            config_destroy(&cfg);
            return -1;
        }

        ret = MeasurementLoad(mm, measurement);
        if (ret != 0) {
            printf("[META] load_measurement failed.\n");
            config_destroy(&cfg);
            return -1;
        }

        ret = MeasurementMgrAdd(mgr, mm);
        if (ret != 0) {
            printf("[META] Add measurements failed.\n");
            config_destroy(&cfg);
            return -1;
        }
    }

    config_destroy(&cfg);
    return 0;
}


int MeasurementMgrLoad(MeasurementMgr *mgr, const char *metaDir)
{
    int ret = 0;
    DIR *d = NULL;
    char metaPath[MAX_META_PATH_LEN] = {0};

    d = opendir(metaDir);
    if (d == NULL) {
        printf("open meta directory failed.\n");
        return -1;
    }

    struct dirent *file = readdir(d);
    while (file != NULL) {
        // skip current dir, parent dir and hidden files
        if(strncmp(file->d_name, ".", 1) == 0) {
            file = readdir(d);
            continue;
        }

        memset(metaPath, 0, sizeof(metaPath));
        snprintf(metaPath, MAX_META_PATH_LEN - 1, "%s/%s", metaDir, file->d_name);
        ret = MeasurementMgrLoadSingleMeta(mgr, metaPath);
        if (ret != 0) {
            printf("[META] load single meta file failed. meta file: %s\n", metaPath);
            closedir(d);
            return -1;
        }

        file = readdir(d);
    }

    closedir(d);
    return 0;
}


