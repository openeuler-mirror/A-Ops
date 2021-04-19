#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

#include "egress.h"

#define DATA_CONSUME_INTERVAL_S 1
#define DATA_RECENT_TIME_S 5

EgressMgr *EgressMgrCreate()
{
    EgressMgr *mgr;
    mgr = (EgressMgr *)malloc(sizeof(EgressMgr));
    if (mgr == NULL) {
        return NULL;
    }

    memset(mgr, 0, sizeof(EgressMgr));
    return mgr;
}

void EgressMgrDestroy(EgressMgr *mgr)
{
    if (mgr == NULL) {
        return;
    }

    free(mgr);
    return;
}

static void EgressDataProcessOne(EgressMgr *mgr, const char *data)
{
    KafkaMgr *kafkaMgr = mgr->kafkaMgr;
    KafkaMsgProduce(kafkaMgr, data, strlen(data));
    printf("[EGRESS] kafka produce one data: %s\n", data);
}

static void EgressDataProcess(EgressMgr *mgr)
{
    TAOS_SUB *tSub = NULL;
    TAOS_ROW row = NULL;
    TAOS_FIELD *fields = NULL;
    TAOS_RES *taosRes = NULL;
    int num_fields = 0;

    char dataBuf[MAX_DATA_STR_LEN];
    TaosDbMgr *taosDbMgr = mgr->taosDbMgr;
    MeasurementMgr *mmMgr = mgr->mmMgr;

    for (int i = 0; i < mmMgr->measurementsNum; i++) {
        taosRes = TaosDbMgrGetRecentRecords(mmMgr->measurements[i]->name, DATA_RECENT_TIME_S, taosDbMgr);
        if (taosRes == NULL) {
            continue;
        }

        num_fields = taos_num_fields(taosRes);
        fields = taos_fetch_fields(taosRes);
        while ((row = taos_fetch_row(taosRes))) {
            memset(dataBuf, 0, MAX_DATA_STR_LEN);
            taos_print_row(dataBuf, row, fields, num_fields);
            EgressDataProcessOne(mgr, dataBuf);
        }
        taos_free_result(taosRes);
    }
    

    /*
    for (int i = 0; i < taosDbMgr->taosSubNum; i++) {
        TAOS_SUB *tSub = taosDbMgr->taosSubs[i];
        TAOS_RES *res = taos_consume(tSub);
        if (res == NULL) {
            continue;
        } else {
            num_fields = taos_num_fields(res);
            fields = taos_fetch_fields(res);
            while ((row = taos_fetch_row(res))) {
                memset(dataBuf, 0, MAX_DATA_STR_LEN);
                taos_print_row(dataBuf, row, fields, num_fields);
                EgressDataProcessOne(mgr, dataBuf);
            }
        }
    }
    */
}

void EgressMain(EgressMgr *mgr)
{
    for (;;) {
        EgressDataProcess(mgr);
        sleep(DATA_CONSUME_INTERVAL_S);
    }
}

