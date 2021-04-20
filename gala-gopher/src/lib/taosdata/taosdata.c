#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "taosdata.h"

static TAOS_RES *TaosExecute(const char *sql, TAOS *taos)
{
    TAOS_RES *res = NULL;
    int t_errno = 0;

    for (int i = 0; i < MAX_TAOS_SQL_RETRY_TIMES; i++) {
        if (res != NULL) {
            taos_free_result(res);
            res = NULL;
        }

        res = taos_query(taos, sql);
        t_errno = taos_errno(res);
        if (t_errno == 0) {
            return res;
        }
    }

    if (t_errno != 0) {
        printf("[TAOS_DATA]Failed to run: %s, reason: %s\n", sql, taos_errstr(res));
        taos_free_result(res);
        return NULL;
    }

    return res;
}


// database operation
int TaosCreateDb(const char *dbName, TAOS *taos)
{
    TAOS_RES *res = NULL;
    char sql[MAX_TAOS_SQL_LEN];
    snprintf(sql, MAX_TAOS_SQL_LEN, "create database %s", dbName);

    res = TaosExecute(sql, taos);
    if (res == NULL) {
        return -1;
    }

    taos_free_result(res);
    return 0;
}

int TaosDropDb(const char *dbName, TAOS *taos)
{
    TAOS_RES *res = NULL;
    char sql[MAX_TAOS_SQL_LEN];
    snprintf(sql, MAX_TAOS_SQL_LEN, "drop database if exists %s", dbName);

    res = TaosExecute(sql, taos);
    if (res == NULL) {
        return -1;
    }

    taos_free_result(res);
    return 0;
}

int TaosSwitchDb(const char *dbName, TAOS *taos)
{
    TAOS_RES *res = NULL;
    char sql[MAX_TAOS_SQL_LEN];
    snprintf(sql, MAX_TAOS_SQL_LEN, "use %s", dbName);

    res = TaosExecute(sql, taos);
    if (res == NULL) {
        return -1;
    }

    taos_free_result(res);
    return 0;

}

// table operation
int TaosCreateTable(const char *tableName, const char *metaStr, TAOS *taos)
{
    TAOS_RES *res = NULL;
    char sql[MAX_TAOS_SQL_LEN];
    snprintf(sql, MAX_TAOS_SQL_LEN, "create table if not exists %s ( ts timestamp %s )", tableName, metaStr);

    res = TaosExecute(sql, taos);
    if (res == NULL) {
        return -1;
    }

    taos_free_result(res);
    return 0;

}

int TaosDropTable(const char *tableName, TAOS *taos)
{
    TAOS_RES *res = NULL;
    char sql[MAX_TAOS_SQL_LEN];
    snprintf(sql, MAX_TAOS_SQL_LEN, "drop database if exists %s", tableName);

    res = TaosExecute(sql, taos);
    if (res == NULL) {
        return -1;
    }

    taos_free_result(res);
    return 0;

}

// record operation
int TaosInsertOneRecord(const char *tableName, const char *dataStr, TAOS *taos)
{
    TAOS_RES *res = NULL;
    char sql[MAX_TAOS_SQL_LEN];
    snprintf(sql, MAX_TAOS_SQL_LEN, "insert into %s values ( now, %s )", tableName, dataStr);

    res = TaosExecute(sql, taos);
    if (res == NULL) {
        return -1;
    }

    taos_free_result(res);
    return 0;
}

// taos database manager
TaosDbMgr *TaosDbMgrCreate(const char *ip, const char *user, const char *pass, const char *db, uint16_t port)
{
    TaosDbMgr *mgr = NULL;
    int ret = 0;
    mgr = (TaosDbMgr *)malloc(sizeof(TaosDbMgr));
    if (mgr == NULL) {
        return NULL;
    }

    // init taos db value
    memcpy(mgr->taosIp, ip, strlen(ip));
    memcpy(mgr->taosUser, user, strlen(user));
    memcpy(mgr->taosPass, pass, strlen(pass));
    memcpy(mgr->taosDbName, db, strlen(db));
    mgr->taosPort = port;

    // connect taosdata
    mgr->taos = taos_connect(ip, user, pass, NULL, port);
    if (mgr->taos == NULL) {
        printf("[TAOS] try to connect taos server failed.\n");
        goto ERR;
    }

    // initialize database
    ret = TaosDropDb(mgr->taosDbName, mgr->taos);
    if (ret != 0) {
        printf("[TAOS] drop database %s failed.\n", mgr->taosDbName);
        goto ERR;
    }

    ret = TaosCreateDb(mgr->taosDbName, mgr->taos);
    if (ret != 0) {
        printf("[TAOS] create database %s failed.\n", mgr->taosDbName);
        goto ERR;
    }

    ret = TaosSwitchDb(mgr->taosDbName, mgr->taos);
    if (ret != 0) {
        printf("[TAOS] use database %s failed.\n", mgr->taosDbName);
        goto ERR;
    }

    return mgr;
ERR:
    TaosDbMgrDestroy(mgr);
    return NULL;
}

void TaosDbMgrDestroy(TaosDbMgr *mgr)
{
    if (mgr == NULL) {
        return;
    }

    if (mgr->taos == NULL) {
        free(mgr);
        return;
    }

    taos_close(mgr->taos);
    taos_cleanup();
    free(mgr);
    return;
}

int TaosDbMgrCreateTable(Measurement *mm, TaosDbMgr *mgr)
{
    int ret = 0;
    char metaStr[MAX_TAOS_SQL_LEN] = {0};
    char metaStrTmp[MAX_TAOS_SQL_LEN] = {0};
    for (int i = 0; i < mm->fieldsNum; i++) {
        // generate create table meta data
        snprintf(metaStr, MAX_TAOS_SQL_LEN, " %s, %s binary(50)", metaStrTmp, mm->fields[i].name);
        snprintf(metaStrTmp, MAX_TAOS_SQL_LEN, " %s", metaStr);
    }
    
    ret = TaosCreateTable(mm->name, metaStr, mgr->taos);
    if (ret != 0) {
        printf("[TAOS] create table %s failed.\n", mm->name);
        return -1;
    }
    printf("[TAOS] create table %s success. \n", mm->name);
    
    return 0;
}

int TaosDbMgrSubscribeTable(Measurement *mm, TaosDbMgr *mgr)
{
    int ret = 0;
    TAOS_SUB *tSub = NULL;
    char sql[MAX_TAOS_SQL_LEN] = "";

    snprintf(sql, MAX_TAOS_SQL_LEN, "select * from %s;", mm->name);
    tSub = taos_subscribe(mgr->taos, 0, mm->name, sql, NULL, NULL, 0);
    if (tSub == NULL) {
        printf("[TAOS] subscribe table %s failed.\n", mm->name);
        return -1;
    }

    mgr->taosSubs[mgr->taosSubNum] = tSub;
    mgr->taosSubNum++;

    return 0;
}

int TaosDbMgrInsertOneRecord(const char *data, TaosDbMgr *mgr)
{
    int ret = 0;
    int i = 0;

    // generate insert data meta data
    char dataStr[MAX_TAOS_SQL_LEN] = {0};
    char mmName[MAX_MEASUREMENT_NAME_LEN];
    int size = strlen(data);
    int index = 0;

    for (i = 1; i < size; i++) {
        if (data[i] == '|') {
            mmName[i - 1] = '\0';
            break;
        } else {
            mmName[i - 1] = data[i];
        }
    }

    // data string start from "
    i++;
    dataStr[index++] = '\"';
    for (; i < size - 2; i++) {    // the last char is '\n', and the (last - 1) char is '|' 
        if (data[i] == '|') {
            dataStr[index++] = '\"';
            dataStr[index++] = ',';
            dataStr[index++] = '\"';
        } else {
            dataStr[index++] = data[i];
        }
    }
    dataStr[index++] = '\"';
    dataStr[index] = '\0';

    ret = TaosInsertOneRecord(mmName, dataStr, mgr->taos);
    if (ret != 0) {
        
        return -1;
    }
    return 0;
}

TAOS_RES *TaosDbMgrGetRecentRecords(const char *tableName, uint32_t time_s, TaosDbMgr *mgr)
{
    time_t seconds;
    TAOS_RES *res = NULL;
    char sql[MAX_TAOS_SQL_LEN];

    seconds = time(NULL); 
    snprintf(sql, MAX_TAOS_SQL_LEN, "select * from %s where ts > %ld;", tableName, (seconds - time_s) * 1000);

    res = TaosExecute(sql, mgr->taos);
    if (res == NULL) {
        return NULL;
    }

    return res;
}

