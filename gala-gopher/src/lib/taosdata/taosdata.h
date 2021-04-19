#ifndef __TAOSDATA_H__
#define __TAOSDATA_H__

#include <stdint.h>
#include <taos.h>

#include "meta.h"
#include "probe_data.h"

#define MAX_TAO

#define MAX_TAOS_IP_LEN 64
#define MAX_TAOS_USER_LEN 64
#define MAX_TAOS_PASS_LEN 64
#define MAX_TAOS_DB_NAME_LEN 64
#define MAX_TAOS_SUB_NUM 1024

typedef struct {
    char taosIp[MAX_TAOS_IP_LEN];
    char taosUser[MAX_TAOS_USER_LEN];
    char taosPass[MAX_TAOS_PASS_LEN];
    char taosDbName[MAX_TAOS_DB_NAME_LEN];
    uint16_t taosPort;
    TAOS *taos;

    uint32_t taosSubNum;
    TAOS_SUB *taosSubs[MAX_TAOS_SUB_NUM];
} TaosDbMgr;

// database operation
int TaosCreateDb(const char *dbName, TAOS *taos);
int TaosDropDb(const char *dbName, TAOS *taos);
int TaosSwitchDb(const char *dbName, TAOS *taos);

// table operation
int TaosCreateTable(const char *tableName, const char *metaStr, TAOS *taos);
int TaosDropTable(const char *tableName, TAOS *taos);

// record operation
int TaosInsertOneRecord(const char *tableName, const char *dataStr, TAOS *taos);

// taos database manager
TaosDbMgr *TaosDbMgrCreate(const char *ip, const char *user, const char *pass, const char *db, uint16_t port);
void TaosDbMgrDestroy(TaosDbMgr *mgr);

int TaosDbMgrCreateTable(Measurement *mm, TaosDbMgr *mgr);
int TaosDbMgrSubscribeTable(Measurement *mm, TaosDbMgr *mgr);
int TaosDbMgrInsertOneRecord(const char *data, TaosDbMgr *mgr);
TAOS_RES *TaosDbMgrGetRecentRecords(const char *tableName, uint32_t time_s, TaosDbMgr *mgr);

#endif

