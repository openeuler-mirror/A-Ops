/******************************************************************************
 * Copyright (c) Huawei Technologies Co., Ltd. 2021. All rights reserved.
 * iSulad licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Author: Hubble_Zhu
 * Create: 2021-04-12
 * Description:
 ******************************************************************************/
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <libconfig.h>
#include "meta.h"

#if GALA_GOPHER_INFO("inner func")
static Measurement *MeasurementCreate(void);
static void MeasurementDestroy(Measurement *mm);
static int MeasurementMgrAdd(MeasurementMgr *mgr, Measurement *measurement);
static Measurement *MeasurementMgrGet(MeasurementMgr *mgr, const char *name);
#endif

static Measurement *MeasurementCreate(void)
{
    Measurement *mm = NULL;
    mm = (Measurement *)malloc(sizeof(Measurement));
    if (mm == NULL)
        return NULL;

    memset(mm, 0, sizeof(Measurement));
    return mm;
}

static void MeasurementDestroy(Measurement *mm)
{
    if (mm == NULL)
        return;

    free(mm);
    return;
}

MeasurementMgr *MeasurementMgrCreate(uint32_t measurementsCapability, uint32_t fields_num_max)
{
    MeasurementMgr *mgr = NULL;
    mgr = (MeasurementMgr *)malloc(sizeof(MeasurementMgr));
    if (mgr == NULL) {
        return NULL;
    }
    memset(mgr, 0, sizeof(MeasurementMgr));

    mgr->measurements = (Measurement **)malloc(sizeof(Measurement *) * measurementsCapability);
    if (mgr->measurements == NULL) {
        free(mgr);
        return NULL;
    }
    memset(mgr->measurements, 0, sizeof(Measurement *) * measurementsCapability);
    mgr->measurementsCapability = measurementsCapability;
    mgr->fields_num_max = fields_num_max < MAX_FIELDS_NUM ? fields_num_max : MAX_FIELDS_NUM;

    return mgr;
}

void MeasurementMgrDestroy(MeasurementMgr *mgr)
{
    if (mgr == NULL)
        return;

    for (int i = 0; i < mgr->measurementsNum; i++) {
        if (mgr->measurements[i] != NULL)
            MeasurementDestroy(mgr->measurements[i]);
    }

    free(mgr->measurements);
    free(mgr);
    return;
}

static int MeasurementMgrAdd(MeasurementMgr *mgr, Measurement *measurement)
{
    Measurement *mm = NULL;
    mm = MeasurementMgrGet(mgr, measurement->name);
    if (mm != NULL)
        return -1;

    if (mgr->measurementsNum == mgr->measurementsCapability) {
        return -1;
    }
    mgr->measurements[mgr->measurementsNum] = measurement;
    mgr->measurementsNum++;
    return 0;
}

static Measurement *MeasurementMgrGet(MeasurementMgr *mgr, const char *name)
{
    for (int i = 0; i < mgr->measurementsNum; i++) {
        if (strcmp(mgr->measurements[i]->name, name) == 0)
            return mgr->measurements[i];
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
        ERROR("load field description failed.\n");
        return -1;
    }
    (void)strncpy(field->description, token, MAX_FIELD_DESCRIPTION_LEN - 1);

    ret = config_setting_lookup_string(fieldConfig, "type", &token);
    if (ret == 0) {
        ERROR("load field type failed.\n");
        return -1;
    }
    (void)strncpy(field->type, token, MAX_FIELD_TYPE_LEN - 1);

    ret = config_setting_lookup_string(fieldConfig, "name", &token);
    if (ret == 0) {
        ERROR("load field name failed.\n");
        return -1;
    }
    (void)strncpy(field->name, token, MAX_FIELD_NAME_LEN - 1);

    return 0;
}

static int MeasurementLoad(MeasurementMgr *mgr, Measurement *mm, config_setting_t *mmConfig)
{
    int ret = 0;
    const char *name;
    const char *field;
    ret = config_setting_lookup_string(mmConfig, "name", &name);
    if (ret == 0) {
        ERROR("load measurement name failed.\n");
        return -1;
    }

    (void)strncpy(mm->name, name, MAX_MEASUREMENT_NAME_LEN - 1);
    config_setting_t *fields = config_setting_lookup(mmConfig, "fields");
    int fieldsCount = config_setting_length(fields);
    if (fieldsCount > mgr->fields_num_max) {
        ERROR("Too many fields.\n");
        return -1;
    }

    for (int i = 0; i < fieldsCount; i++) {
        config_setting_t *fieldConfig = config_setting_get_elem(fields, i);

        ret = FieldLoad(&mm->fields[i], fieldConfig);
        if (ret != 0)
            ERROR("[META] load measurement field failed.\n");

        mm->fieldsNum++;
    }

    return 0;
}

int MeasurementMgrLoadSingleMeta(MeasurementMgr *mgr, const char *metaPath)
{
    int ret = 0;
    config_t cfg;
    config_setting_t *measurements = NULL;
    const char *version = NULL;

    char *name = NULL;
    char *field = NULL;

    INFO("[META] begin load meta: %s.\n", metaPath);

    config_init(&cfg);
    ret = config_read_file(&cfg, metaPath);
    if (ret == 0) {
        ERROR("[META] config read file %s failed.\n", metaPath);
        config_destroy(&cfg);
        return -1;
    }

    ret = config_lookup_string(&cfg, "version", &version);
    if (ret <= 0) {
        ERROR("[META] get version failed.\n");
        config_destroy(&cfg);
        return -1;
    }

    measurements = config_lookup(&cfg, "measurements");
    if (measurements == NULL) {
        ERROR("[META] get measurements failed.\n");
        config_destroy(&cfg);
        return -1;
    }

    int count = config_setting_length(measurements);
    for (int i = 0; i < count; i++) {
        config_setting_t *measurement = config_setting_get_elem(measurements, i);

        Measurement *mm = MeasurementCreate();
        if (mm == NULL) {
            ERROR("[META] malloc measurement failed.\n");
            config_destroy(&cfg);
            return -1;
        }
        (void)memset(mm->version, 0, MAX_META_VERSION_LEN);
        (void)strncpy(mm->version, version, MAX_META_VERSION_LEN - 1);

        ret = MeasurementLoad(mgr, mm, measurement);
        if (ret != 0) {
            ERROR("[META] load_measurement failed.\n");
            config_destroy(&cfg);
            MeasurementDestroy(mm);
            return -1;
        }

        ret = MeasurementMgrAdd(mgr, mm);
        if (ret != 0) {
            ERROR("[META] Add measurements failed.\n");
            config_destroy(&cfg);
            MeasurementDestroy(mm);
            return -1;
        }
    }

    config_destroy(&cfg);
    return 0;
}

int MeasurementMgrLoad(const MeasurementMgr *mgr, const char *metaDir)
{
    int ret = 0;
    DIR *d = NULL;
    char metaPath[MAX_META_PATH_LEN] = {0};

    d = opendir(metaDir);
    if (d == NULL) {
        ERROR("open meta directory failed.\n");
        return -1;
    }

    struct dirent *file = readdir(d);
    while (file != NULL) {
        // skip current dir, parent dir and hidden files
        if (strncmp(file->d_name, ".", 1) == 0) {
            file = readdir(d);
            continue;
        }

        memset(metaPath, 0, sizeof(metaPath));
        (void)snprintf(metaPath, MAX_META_PATH_LEN - 1, "%s/%s", metaDir, file->d_name);
        ret = MeasurementMgrLoadSingleMeta((MeasurementMgr *)mgr, metaPath);
        if (ret != 0) {
            ERROR("[META] load single meta file failed. meta file: %s\n", metaPath);
            closedir(d);
            return -1;
        }

        file = readdir(d);
    }

    closedir(d);
    return 0;
}
