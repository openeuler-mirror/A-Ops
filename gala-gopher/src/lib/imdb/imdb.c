#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#include "imdb.h"

int g_recordTimeout = 60;       // default timeout: 60 seconds

IMDB_Metric *IMDB_MetricCreate(char *name, char *description, char *type)
{
    int ret = 0;
    IMDB_Metric *metric = NULL;
    metric = (IMDB_Metric *)malloc(sizeof(IMDB_Metric));
    if (metric == NULL) {
        return NULL;
    }

    memset(metric, 0, sizeof(IMDB_Metric));
    ret = snprintf(metric->name, MAX_IMDB_METRIC_NAME_LEN, name);
    if (ret < 0) {
        free(metric);
        return NULL;
    }

    ret = snprintf(metric->description, MAX_IMDB_METRIC_DESC_LEN, description);
    if (ret < 0) {
        free(metric);
        return NULL;
    }

    ret = snprintf(metric->type, MAX_IMDB_METRIC_TYPE_LEN, type);
    if (ret < 0) {
        free(metric);
        return NULL;
    }

    return metric;
}

int IMDB_MetricSetValue(IMDB_Metric *metric, char *val)
{
    int ret = 0;
    ret = snprintf(metric->val, MAX_IMDB_METRIC_VAL_LEN, val);
    if (ret < 0) {
        return -1;
    }

    return 0;
}

void IMDB_MetricDestroy(IMDB_Metric *metric)
{
    if (metric == NULL) {
        return;
    }

    free(metric);
    return;
}

IMDB_Record *IMDB_RecordCreate(uint32_t capacity)
{
    IMDB_Record *record = NULL;
    record = (IMDB_Record *)malloc(sizeof(IMDB_Record));
    if (record == NULL) {
        return NULL;
    }
    memset(record, 0, sizeof(IMDB_Record));

    record->metrics = (IMDB_Metric **)malloc(sizeof(IMDB_Metric *) * capacity);
    if (record->metrics == NULL) {
        free(record);
        return NULL;
    }
    memset(record->metrics, 0, sizeof(IMDB_Metric *) * capacity);

    record->capacity = capacity;
    return record;
}

IMDB_Record *IMDB_RecordCreateWithKey(uint32_t capacity, uint32_t keySize)
{
    IMDB_Record *record = IMDB_RecordCreate(capacity);
    if (record != NULL) {
        record->key = (char *)malloc(sizeof(char) * keySize);
        if (record->key == NULL) {
            IMDB_RecordDestroy(record);
            return NULL;
        }
        memset(record->key, 0, sizeof(char) * keySize);
        record->keySize = keySize;
    }

    return record;
}

int IMDB_RecordAddMetric(IMDB_Record *record, IMDB_Metric *metric)
{
    if (record->metricsNum == record->capacity) {
        return -1;
    }

    record->metrics[record->metricsNum] = metric;
    record->metricsNum++;
    return 0;
}

int IMDB_RecordAppendKey(IMDB_Record *record, uint32_t keyIdx, char *val)
{
    int ret = 0;
    uint32_t offset = keyIdx * MAX_IMDB_METRIC_VAL_LEN;

    if (offset + MAX_IMDB_METRIC_VAL_LEN > record->keySize) {
        return -1;
    }

    ret = snprintf(record->key + offset, MAX_IMDB_METRIC_VAL_LEN, val);
    if (ret < 0) {
        return -1;
    }

    return 0;
}

void IMDB_RecordUpdateTime(IMDB_Record *record, time_t seconds)
{
    record->updateTime = seconds;
    return;
}

void IMDB_RecordDestroy(IMDB_Record *record)
{
    if (record == NULL) {
        return;
    }

    if (record->key != NULL) {
        free(record->key);
    }

    if (record->metrics != NULL) {
        for (int i = 0; i < record->metricsNum; i++) {
            IMDB_MetricDestroy(record->metrics[i]);
        }
        free(record->metrics);
    }
    free(record);
    return;
}

IMDB_Table *IMDB_TableCreate(char *name, uint32_t capacity)
{
    IMDB_Table *table = NULL;
    table = (IMDB_Table *)malloc(sizeof(IMDB_Table));
    if (table == NULL) {
        return NULL;
    }
    memset(table, 0, sizeof(IMDB_Table));

    table->records = (IMDB_Record **)malloc(sizeof(IMDB_Record *));
    if (table->records == NULL) {
        free(table);
        return NULL;
    }
    *table->records = NULL;     // necessary

    table->recordsCapacity = capacity;
    memcpy(table->name, name, strlen(name));
    return table;
}

int IMDB_TableSetMeta(IMDB_Table *table, IMDB_Record *metaRecord)
{
    table->meta = metaRecord;
    return 0;
}

int IMDB_TableSetRecordKeySize(IMDB_Table *table, uint32_t keyNum)
{
    table->recordKeySize = keyNum * MAX_IMDB_METRIC_VAL_LEN;
    return 0;
}

int IMDB_TableAddRecord(IMDB_Table *table, IMDB_Record *record)
{
    IMDB_Record *old_record;

    old_record = HASH_findRecord(table->records, record);
    if (old_record != NULL) {
        HASH_deleteRecord(table->records, old_record);
        IMDB_RecordDestroy(old_record);
    }

    if (HASH_recordCount(table->records) >= table->recordsCapacity) {
        printf("[IMDB] Can not add new record to table %s: table full.\n", table->name);
        return -1;
    }
    IMDB_RecordUpdateTime(record, time(NULL));
    HASH_addRecord(table->records, record);

    return 0;
}

void IMDB_TableDestroy(IMDB_Table *table)
{
    if (table == NULL) {
        return;
    }

    if (table->records != NULL) {
        HASH_deleteAndFreeRecords(table->records);
        free(table->records);
    }

    if (table->meta != NULL) {
        IMDB_RecordDestroy(table->meta);
    }

    free(table);
    return;
}

static int IMDB_GetMachineId(char *buffer, size_t size)
{
    FILE *fp = NULL;

    fp = popen("cat /etc/machine-id", "r");
    if (fp == NULL) {
        return -1;
    }

    buffer = fgets(buffer, size, fp);
    if (buffer == NULL) {
        pclose(fp);
        return -1;
    }
    if (strlen(buffer) > 0 && buffer[strlen(buffer) - 1] == '\n') {
        buffer[strlen(buffer) - 1] = '\0';
    }

    pclose(fp);
    return 0;
}

IMDB_DataBaseMgr *IMDB_DataBaseMgrCreate(uint32_t capacity)
{
    int ret = 0;
    IMDB_DataBaseMgr *mgr = NULL;
    mgr = (IMDB_DataBaseMgr *)malloc(sizeof(IMDB_DataBaseMgr));
    if (mgr == NULL) {
        return NULL;
    }
    memset(mgr, 0, sizeof(IMDB_DataBaseMgr));

    ret = IMDB_GetMachineId(mgr->nodeInfo.machineId, sizeof(mgr->nodeInfo.machineId));
    if (ret != 0) {
        printf("[IMDB] Can not get machine id.\n");
        free(mgr);
        return NULL;
    }

    ret = gethostname(mgr->nodeInfo.hostName, sizeof(mgr->nodeInfo.hostName));
    if (ret != 0) {
        free(mgr);
        return NULL;
    }

    mgr->tables = (IMDB_Table **)malloc(sizeof(IMDB_Table *) * capacity);
    if (mgr->tables == NULL) {
        free(mgr);
        return NULL;
    }
    memset(mgr->tables, 0, sizeof(IMDB_Table *) * capacity);

    mgr->capacity = capacity;
    ret = pthread_rwlock_init(&mgr->rwlock, NULL);
    if (ret != 0) {
        free(mgr->tables);
        free(mgr);
        return NULL;
    }

    return mgr;
}

void IMDB_DataBaseMgrSetRecordTimeout(uint32_t timeout)
{
    if (timeout > 0) {
        g_recordTimeout = timeout;
    }
    return;
}

void IMDB_DataBaseMgrDestroy(IMDB_DataBaseMgr *mgr)
{
    if (mgr == NULL) {
        return;
    }

    if (mgr->tables != NULL) {
        for (int i = 0; i < mgr->tablesNum; i++) {
            IMDB_TableDestroy(mgr->tables[i]);
        }
        free(mgr->tables);
    }

    free(mgr);
    return;
}

int IMDB_DataBaseMgrAddTable(IMDB_DataBaseMgr *mgr, IMDB_Table* table)
{
    if (mgr->tablesNum == mgr->capacity) {
        return -1;
    }

    for (int i = 0; i < mgr->tablesNum; i++) {
        if (strcmp(mgr->tables[i]->name, table->name) == 0) {
            return -1;
        }
    }

    mgr->tables[mgr->tablesNum] = table;
    mgr->tablesNum++;
    return 0;
}

IMDB_Table *IMDB_DataBaseMgrFindTable(IMDB_DataBaseMgr *mgr, char *tableName)
{
    for (int i = 0; i < mgr->tablesNum; i++) {
        if (strcmp(mgr->tables[i]->name, tableName) == 0) {
            return mgr->tables[i];
        }
    }

    return NULL;
}

int IMDB_DataBaseMgrAddRecord(IMDB_DataBaseMgr *mgr, char *recordStr, int len)
{
    pthread_rwlock_wrlock(&mgr->rwlock);

    int ret = 0;
    IMDB_Table *table = NULL;
    IMDB_Record *record = NULL;
    IMDB_Metric *metric = NULL;

    int index = -1;
    char *token = NULL;
    char delim[] = "|";
    char *buffer = NULL;
    char *buffer_head = NULL;

    uint32_t keyIdx = 0;

    buffer = strdup(recordStr);
    if (buffer == NULL) {
        goto ERR;
    }
    buffer_head = buffer;

    // start analyse record string
    for (token = strsep(&buffer, delim); token != NULL; token = strsep(&buffer, delim)) {
        if (strcmp(token, "") == 0) {
            continue;
        }
        if (strcmp(token, "\n") == 0) {
            continue;
        }

        // mark table name as the -1 substring so that metrics start at 0
        // find table by the first substring
        if (index == -1) {
            table = IMDB_DataBaseMgrFindTable(mgr, token);
            if (table == NULL) {
                printf("[IMDB] Can not find table named %s.\n", token);
                free(buffer_head);
                goto ERR;
            }

            if (table->recordKeySize == 0) {
                printf("[IMDB] Can not add record to table %s: no key type of metric set.\n", token);
                free(buffer_head);
                goto ERR;
            }

            record = IMDB_RecordCreateWithKey(MAX_IMDB_RECORD_CAPACITY, table->recordKeySize);
            if (record == NULL) {
                printf("[IMDB] Can not create record.\n");
                free(buffer_head);
                goto ERR;
            }

            index += 1;
            continue;
        }

        // fill record by the rest substrings
        metric = IMDB_MetricCreate(table->meta->metrics[index]->name,
                                   table->meta->metrics[index]->description,
                                   table->meta->metrics[index]->type);
        if (metric == NULL) {
            printf("[IMDB] Can't create metrics.\n");
            free(buffer_head);
            goto ERR;
        }

        ret = IMDB_MetricSetValue(metric, token);
        if (ret != 0) {
            free(buffer_head);
            goto ERR;
        }

        ret = IMDB_RecordAddMetric(record, metric);
        if (ret != 0) {
            free(buffer_head);
            goto ERR;
        }

        if (strcmp(METRIC_TYPE_KEY, table->meta->metrics[index]->type) == 0) {
            ret = IMDB_RecordAppendKey(record, keyIdx, token);
            if (ret < 0) {
                printf("[IMDB] Can not set record key.\n");
                free(buffer_head);
                goto ERR;
            }
            keyIdx++;
        }

        index += 1;
    }

    ret = IMDB_TableAddRecord(table, record);
    if (ret != 0) {
        free(buffer_head);
        goto ERR;
    }

    // printf("[IMDB] Add Record success.\n");
    free(buffer_head);

    pthread_rwlock_unlock(&mgr->rwlock);
    return 0;
ERR:
    pthread_rwlock_unlock(&mgr->rwlock);
    if (record != NULL) {
        IMDB_RecordDestroy(record);
    }
    return -1;
}

static int IMDB_MetricDescription2String(IMDB_Metric *metric, char *buffer, int maxLen, char *tableName)
{
    return snprintf(buffer, maxLen, "# HELP gala_gopher_%s_%s %s\n", tableName, metric->name, metric->description);
}

static int IMDB_MetricType2String(IMDB_Metric *metric, char *buffer, int maxLen, char *tableName)
{
    return snprintf(buffer, maxLen, "# TYPE gala_gopher_%s_%s %s\n", tableName, metric->name, metric->type);
}

static int IMDB_MetricValue2String(IMDB_Metric *metric, char *buffer, int maxLen, char *tableName, char *labels)
{
    time_t now;
    time(&now);
    return snprintf(buffer, maxLen, "gala_gopher_%s_%s%s %s %lld\n", tableName, metric->name, labels, metric->val, now * 1000);
}

static int IMDB_Metric2String(IMDB_Metric *metric, char *buffer, int maxLen, char *tableName, char *labels)
{
    int ret = 0;
    int total = 0;
    ret = IMDB_MetricDescription2String(metric, buffer, maxLen, tableName);
    if (ret < 0) {
        return -1;
    }
    buffer += ret;
    maxLen -= ret;
    total += ret;

    ret = IMDB_MetricType2String(metric, buffer, maxLen, tableName);
    if (ret < 0) {
        return -1;
    }
    buffer += ret;
    maxLen -= ret;
    total += ret;

    ret = IMDB_MetricValue2String(metric, buffer, maxLen, tableName, labels);
    if (ret < 0) {
        return -1;
    }
    total += ret;

    return total;
}

// return 0 if satisfy, return -1 if not
static int MetricTypeSatisfyPrometheus(IMDB_Metric *metric)
{
    const char prometheusTypes[][MAX_IMDB_METRIC_TYPE_LEN] = {
        "counter",
        "gauge",
        "histogram",
        "summary"
    };

    int size = sizeof(prometheusTypes) / sizeof(prometheusTypes[0]);
    for (int i = 0; i < size; i++) {
        if (strcmp(metric->type, prometheusTypes[i]) == 0) {
            return 0;
        }
    }

    return -1;
}

static int MetricTypeIsLabel(IMDB_Metric *metric)
{
    const char *label[] = {METRIC_TYPE_LABEL, METRIC_TYPE_KEY};
    for (int i = 0; i < sizeof(label)/sizeof(label[0]); i++) {
        if (strcmp(metric->type, label[i]) == 0) {
            return 1;
        }
    }

    return 0;
}

//name{label1="label1",label2="label2",label2="label2"} value time
static int IMDB_Prometheus_BuildLabel(IMDB_DataBaseMgr *mgr, IMDB_Record *record, char *buffer, int maxLen)
{
    char labels[MAX_LABELS_BUFFER_SIZE] = {0};
    int labell = MAX_LABELS_BUFFER_SIZE;
    int ret = 0;
    int total = 0;
    char write_comma = 0;

    for (int i = 0; i < record->metricsNum; i++) {
        ret = MetricTypeIsLabel(record->metrics[i]);
        if (ret == 0) {
            continue;
        }

        if (write_comma)
        {
            ret = snprintf(labels + total, labell, "%s", ",");
            if (ret < 0) {
                goto ERR;
            }
            total += ret; 
            labell -= ret;          
        }

        ret = snprintf(labels + total, labell, "%s=\"%s\"", record->metrics[i]->name, record->metrics[i]->val);
        if (ret <= 0)
        {
            goto ERR;
        }
        total += ret;
        labell -= ret; 
        write_comma = 1;
    }

    if (total > 0)
    {
        // append machine_id and hostname
        ret = snprintf(labels + total, labell, ",%s=\"%s\",%s=\"%s\"",
                       "machine_id", mgr->nodeInfo.machineId,
                       "hostname", mgr->nodeInfo.hostName);
        if (ret <= 0) {
            goto ERR;
        }

        ret = snprintf(buffer, maxLen, "{%s}", labels);
        if (ret < 0) {
            goto ERR;
        }
        maxLen -= ret;
    }

ERR:
    return ret;
}

static int IMDB_Record2String(IMDB_DataBaseMgr *mgr, IMDB_Record *record, char *buffer, int maxLen, char *tableName)
{
    int ret = 0;
    int total = 0;
    
    char labels[MAX_LABELS_BUFFER_SIZE] = {0};
    ret = IMDB_Prometheus_BuildLabel(mgr, record, labels, MAX_LABELS_BUFFER_SIZE);
    if (ret < 0)
    {
        goto ERR;
    }

    for (int i = 0; i < record->metricsNum; i++) {
        ret = MetricTypeSatisfyPrometheus(record->metrics[i]);
        if (ret != 0) {
            continue;
        }

        ret = IMDB_Metric2String(record->metrics[i], buffer, maxLen, tableName, labels);
        if (ret < 0) {
            return -1;
        }
        buffer += ret;
        maxLen -= ret;
        total += ret;
    }

ERR:
    return total;
}

static int IMDB_Table2String(IMDB_DataBaseMgr *mgr, IMDB_Table *table, char *buffer, int maxLen)
{
    int ret = 0;
    int total = 0;
    IMDB_Record *record, *tmp;

    if (HASH_recordCount(table->records) == 0) {
        return 0;
    }

    HASH_ITER(hh, *table->records, record, tmp) {
        // check timeout
        if (record->updateTime + g_recordTimeout < time(NULL)) {
            // remove invalid record
            HASH_deleteRecord(table->records, record);
            IMDB_RecordDestroy(record);
            continue;
        }

        ret = IMDB_Record2String(mgr, record, buffer, maxLen, table->name);
        if (ret < 0) {
            return -1;
        }
        buffer += ret;
        maxLen -= ret;
        total += ret;
    }    

    ret = snprintf(buffer, maxLen, "\n");
    if (ret < 0) {
        return -1;
    }
    buffer += 1;
    maxLen -= 1;
    total += 1;

    return total;
}

int IMDB_DataBaseMgrData2String(IMDB_DataBaseMgr *mgr, char *buffer, int maxLen)
{
    pthread_rwlock_rdlock(&mgr->rwlock);

    int ret = 0;
    char *cursor = buffer;
    memset(cursor, 0, maxLen);

    for (int i = 0; i < mgr->tablesNum; i++) {
        ret = IMDB_Table2String(mgr, mgr->tables[i], buffer, maxLen);
        if (ret < 0) {
            goto ERR;
        }
        buffer += ret;
        maxLen -= ret;
    }

    pthread_rwlock_unlock(&mgr->rwlock);
    return 0;
ERR:

    pthread_rwlock_unlock(&mgr->rwlock);
    return -1;
}

static int IMDB_Record2Json(IMDB_DataBaseMgr *mgr, IMDB_Table *table, IMDB_Record *record, char *jsonStr, int jsonStrLen)
{
    int ret = 0;
    char buffer[MAX_DATA_STR_LEN];
    char *json_cursor = jsonStr;
    int maxLen = jsonStrLen;

    time_t now;
    time(&now);

    memset(jsonStr, 0, jsonStrLen);
    ret = snprintf(json_cursor, maxLen, "{\"timestamp\": %lld", now * 1000);
    if (ret < 0) {
        return -1;
    }
    json_cursor += ret;
    maxLen -= ret;

    ret = snprintf(json_cursor, maxLen, ", \"machine_id\": \"%s\"", mgr->nodeInfo.machineId);
    if (ret < 0) {
        return -1;
    }
    json_cursor += ret;
    maxLen -= ret;

    ret = snprintf(json_cursor, maxLen, ", \"hostname\": \"%s\"", mgr->nodeInfo.hostName);
    if (ret < 0) {
        return -1;
    }
    json_cursor += ret;
    maxLen -= ret;

    ret = snprintf(json_cursor, maxLen, ", \"table_name\": \"%s\"", table->name);
    if (ret < 0) {
        return -1;
    }
    json_cursor += ret;
    maxLen -= ret;

    for (int i = 0; i < record->metricsNum; i++) {
        ret = snprintf(json_cursor, maxLen, ", \"%s\": \"%s\"", record->metrics[i]->name, record->metrics[i]->val);
        if (ret < 0) {
            return -1;
        }
        json_cursor += ret;
        maxLen -= ret;
    }

    ret = snprintf(json_cursor, maxLen, "}");
    if (ret < 0) {
        return -1;
    }
    json_cursor += ret;
    maxLen -= ret;

    return 0;
}

int IMDB_DataStr2Json(IMDB_DataBaseMgr *mgr, char *recordStr, int recordLen, char *jsonStr, int jsonStrLen)
{
    pthread_rwlock_wrlock(&mgr->rwlock);

    int ret = 0;
    IMDB_Table *table = NULL;
    IMDB_Record *record = NULL;
    IMDB_Metric *metric = NULL;

    int index = -1;
    char *token = NULL;
    char delim[] = "|";
    char *buffer = NULL;
    char *buffer_head = NULL;

    buffer = strdup(recordStr);
    if (buffer == NULL) {
        goto ERR;
    }
    buffer_head = buffer;

    // start analyse record string
    for (token = strsep(&buffer, delim); token != NULL; token = strsep(&buffer, delim)) {
        if (strcmp(token, "") == 0) {
            continue;
        }
        if (strcmp(token, "\n") == 0) {
            continue;
        }

        // mark table name as the -1 substring so that metrics start at 0
        // find table by the first substring
        if (index == -1) {
            table = IMDB_DataBaseMgrFindTable(mgr, token);
            if (table == NULL) {
                printf("[IMDB] Can not find table named %s.\n", token);
                free(buffer_head);
                goto ERR;
            }

            record = IMDB_RecordCreate(MAX_IMDB_RECORD_CAPACITY);
            if (record == NULL) {
                free(buffer_head);
                goto ERR;
            }

            index += 1;
            continue;
        }

        // fill record by the rest substrings
        metric = IMDB_MetricCreate(table->meta->metrics[index]->name,
                                   table->meta->metrics[index]->description,
                                   table->meta->metrics[index]->type);
        if (metric == NULL) {
            printf("[IMDB] Can't create metrics.\n");
            free(buffer_head);
            goto ERR;
        }

        ret = IMDB_MetricSetValue(metric, token);
        if (ret != 0) {
            free(buffer_head);
            goto ERR;
        }

        ret = IMDB_RecordAddMetric(record, metric);
        if (ret != 0) {
            free(buffer_head);
            goto ERR;
        }

        index += 1;
    }

    ret = IMDB_Record2Json(mgr, table, record, jsonStr, jsonStrLen);
    if (ret != 0) {
        free(buffer_head);
        goto ERR;
    }

    // printf("[IMDB] Add Record success.\n");
    free(buffer_head);

    pthread_rwlock_unlock(&mgr->rwlock);
    return 0;
ERR:
    pthread_rwlock_unlock(&mgr->rwlock);
    IMDB_RecordDestroy(record);
    return -1;

}

IMDB_Record *HASH_findRecord(IMDB_Record **records, IMDB_Record *record)
{
    IMDB_Record *r;
    HASH_FIND(hh, *records, record->key, record->keySize, r);
    return r;
}

void HASH_addRecord(IMDB_Record **records, IMDB_Record *record)
{
    HASH_ADD_KEYPTR(hh, *records, record->key, record->keySize, record);
    return;
}

void HASH_deleteRecord(IMDB_Record **records, IMDB_Record *record)
{
    if (records == NULL || record == NULL) {
        return;
    }

    HASH_DEL(*records, record);
    return;
}

void HASH_deleteAndFreeRecords(IMDB_Record **records)
{
    if (records == NULL) {
        return;
    }

    IMDB_Record *r, *tmp;
    HASH_ITER(hh, *records, r, tmp) {
        HASH_deleteRecord(records, r);
        IMDB_RecordDestroy(r);
    }
    return;
}

uint32_t HASH_recordCount(IMDB_Record **records)
{
    uint32_t num = 0;
    num = HASH_COUNT(*records);
    return num;
}