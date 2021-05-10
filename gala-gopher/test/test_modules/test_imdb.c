#include <stdint.h>
#include <CUnit/Basic.h>

#include "imdb.h"
#include "test_imdb.h"

#if GALA_GOPHER_INFO("test cases")
void TestIMDB_MetricCreate();
void TestIMDB_MetricSetValue();
void TestIMDB_RecordCreate();
void TestIMDB_RecordAddMetric();
void TestIMDB_TableCreate();
void TestIMDB_TableSetMeta();
void TestIMDB_TableAddRecord();
void TestIMDB_DataBaseMgrCreate();
void TestIMDB_DataBaseMgrAddTable();
void TestIMDB_DataBaseMgrFindTable();
void TestIMDB_DataBaseMgrAddRecord();
void TestIMDB_DataBaseMgrData2String();
#endif

void TestIMDB_MetricCreate()
{
    IMDB_Metric *metric = IMDB_MetricCreate("aa", "bb", "cc");
    CU_ASSERT(metric != NULL);
    CU_ASSERT(strcmp(metric->name, "aa") == 0);
    CU_ASSERT(strcmp(metric->description, "bb") == 0);
    CU_ASSERT(strcmp(metric->type, "cc") == 0);

    IMDB_MetricDestroy(metric);
}

void TestIMDB_MetricSetValue()
{
    int ret = 0;
    IMDB_Metric *metric = IMDB_MetricCreate("aa", "bb", "cc");
    CU_ASSERT(metric != NULL);

    ret = IMDB_MetricSetValue(metric, "dd");
    CU_ASSERT(ret == 0);
    CU_ASSERT(strcmp(metric->val, "dd") == 0);

    IMDB_MetricDestroy(metric);
}

void TestIMDB_RecordCreate()
{
    IMDB_Record *record = IMDB_RecordCreate(1024);
    CU_ASSERT(record != NULL);
    CU_ASSERT(record->metrics != NULL);
    CU_ASSERT(record->capacity == 1024);
    CU_ASSERT(record->metricsNum == 0);

    IMDB_RecordDestroy(record);
}

void TestIMDB_RecordAddMetric()
{
    int ret = 0;
    IMDB_Record *record = IMDB_RecordCreate(1024);
    CU_ASSERT(record != NULL);

    IMDB_Metric *metric = IMDB_MetricCreate("aa", "bb", "cc");
    CU_ASSERT(metric != NULL);

    ret = IMDB_RecordAddMetric(record, metric);
    CU_ASSERT(ret == 0);
    CU_ASSERT(record->metricsNum == 1);
    CU_ASSERT(record->metrics[0] == metric);

    IMDB_RecordDestroy(record);
}

void TestIMDB_TableCreate()
{
    IMDB_Table *table = IMDB_TableCreate("table1", 1024);
    CU_ASSERT(table != NULL);
    CU_ASSERT(table->records != NULL);
    CU_ASSERT(table->recordsCapacity == 1024);
    CU_ASSERT(table->recordsNum == 0);
    CU_ASSERT(strcmp(table->name, "table1") == 0);
    CU_ASSERT(table->meta == NULL);

    IMDB_TableDestroy(table);
}

void TestIMDB_TableSetMeta()
{
    int ret = 0;
    IMDB_Table *table = IMDB_TableCreate("table1", 1024);
    CU_ASSERT(table != NULL);

    IMDB_Record *record = IMDB_RecordCreate(1024);
    CU_ASSERT(record != NULL);

    IMDB_Metric *metric = IMDB_MetricCreate("aa", "bb", "cc");
    CU_ASSERT(metric != NULL);

    ret = IMDB_RecordAddMetric(record, metric);
    CU_ASSERT(ret == 0);

    ret = IMDB_TableSetMeta(table, record);
    CU_ASSERT(ret == 0);
    CU_ASSERT(table->meta == record);

    IMDB_TableDestroy(table);
}

void TestIMDB_TableAddRecord()
{
    int ret = 0;
    IMDB_Table *table = IMDB_TableCreate("table1", 1024);
    CU_ASSERT(table != NULL);

    IMDB_Record *record = IMDB_RecordCreate(1024);
    CU_ASSERT(record != NULL);

    IMDB_Metric *metric = IMDB_MetricCreate("aa", "bb", "cc");
    CU_ASSERT(metric != NULL);

    ret = IMDB_RecordAddMetric(record, metric);
    CU_ASSERT(ret == 0);

    ret = IMDB_TableAddRecord(table, record);
    CU_ASSERT(ret == 0);
    CU_ASSERT(table->recordsNum == 1);
    CU_ASSERT(table->records[0] == record);

    IMDB_TableDestroy(table);
}

void TestIMDB_DataBaseMgrCreate()
{
    IMDB_DataBaseMgr *mgr = IMDB_DataBaseMgrCreate(1024);
    CU_ASSERT(mgr != NULL);
    CU_ASSERT(mgr->tables != NULL);
    CU_ASSERT(mgr->capacity == 1024);
    CU_ASSERT(mgr->tablesNum == 0);

    IMDB_DataBaseMgrDestroy(mgr);
}

void TestIMDB_DataBaseMgrAddTable()
{
    int ret = 0;
    IMDB_DataBaseMgr *mgr = IMDB_DataBaseMgrCreate(1024);
    CU_ASSERT(mgr != NULL);

    IMDB_Table *table = IMDB_TableCreate("table1", 1024);
    CU_ASSERT(table != NULL);

    ret = IMDB_DataBaseMgrAddTable(mgr, table);
    CU_ASSERT(ret == 0);
    CU_ASSERT(mgr->tablesNum == 1);
    CU_ASSERT(mgr->tables[0] == table);

    IMDB_DataBaseMgrDestroy(mgr);
}

void TestIMDB_DataBaseMgrFindTable()
{
    int ret = 0;
    IMDB_DataBaseMgr *mgr = IMDB_DataBaseMgrCreate(1024);
    CU_ASSERT(mgr != NULL);

    IMDB_Table *table = IMDB_TableCreate("table1", 1024);
    CU_ASSERT(table != NULL);

    ret = IMDB_DataBaseMgrAddTable(mgr, table);
    CU_ASSERT(ret == 0);

    IMDB_Table *tmpTable = IMDB_DataBaseMgrFindTable(mgr, "table1");
    CU_ASSERT(tmpTable == table);

    IMDB_DataBaseMgrDestroy(mgr);
}

void TestIMDB_DataBaseMgrAddRecord()
{
    int ret = 0;
    IMDB_DataBaseMgr *mgr = IMDB_DataBaseMgrCreate(1024);
    CU_ASSERT(mgr != NULL);

    IMDB_Table *table = IMDB_TableCreate("table1", 1024);
    CU_ASSERT(table != NULL);

    IMDB_Record *meta = IMDB_RecordCreate(1024);
    CU_ASSERT(meta != NULL);
    IMDB_Metric *metric1 = IMDB_MetricCreate("metric1", "desc1", "type1");
    CU_ASSERT(metric1 != NULL);
    ret = IMDB_RecordAddMetric(meta, metric1);
    CU_ASSERT(ret == 0);
    IMDB_Metric *metric2 = IMDB_MetricCreate("metric2", "desc2", "type2");
    CU_ASSERT(metric2 != NULL);
    ret = IMDB_RecordAddMetric(meta, metric1);
    CU_ASSERT(ret == 0);
    IMDB_Metric *metric3 = IMDB_MetricCreate("metric3", "desc3", "type3");
    CU_ASSERT(metric3 != NULL);
    ret = IMDB_RecordAddMetric(meta, metric1);
    CU_ASSERT(ret == 0);

    ret = IMDB_TableSetMeta(table, meta);
    CU_ASSERT(ret == 0);

    ret = IMDB_DataBaseMgrAddTable(mgr, table);
    CU_ASSERT(ret == 0);

    char recordStr[] = "|table1|value1|value2|value3|";
    ret = IMDB_DataBaseMgrAddRecord(mgr, recordStr, strlen(recordStr));
    CU_ASSERT(ret == 0);
    CU_ASSERT(table->records[0]->metricsNum == 3);
    CU_ASSERT(strcmp(table->records[0]->metrics[0]->name, "metric1") == 0);
    CU_ASSERT(strcmp(table->records[0]->metrics[0]->description, "desc1") == 0);
    CU_ASSERT(strcmp(table->records[0]->metrics[0]->type, "type1") == 0);
    CU_ASSERT(strcmp(table->records[0]->metrics[0]->val, "value1") == 0);

    CU_ASSERT(strcmp(table->records[0]->metrics[1]->name, "metric2") == 0);
    CU_ASSERT(strcmp(table->records[0]->metrics[1]->description, "desc2") == 0);
    CU_ASSERT(strcmp(table->records[0]->metrics[1]->type, "type2") == 0);
    CU_ASSERT(strcmp(table->records[0]->metrics[1]->val, "value2") == 0);

    CU_ASSERT(strcmp(table->records[0]->metrics[2]->name, "metric3") == 0);
    CU_ASSERT(strcmp(table->records[0]->metrics[2]->description, "desc3") == 0);
    CU_ASSERT(strcmp(table->records[0]->metrics[2]->type, "type3") == 0);
    CU_ASSERT(strcmp(table->records[0]->metrics[2]->val, "value3") == 0);

    IMDB_DataBaseMgrDestroy(mgr);

}

void TestIMDB_DataBaseMgrData2String()
{
    int ret = 0;
    IMDB_DataBaseMgr *mgr = IMDB_DataBaseMgrCreate(1024);
    CU_ASSERT(mgr != NULL);

    IMDB_Table *table = IMDB_TableCreate("table1", 1024);
    CU_ASSERT(table != NULL);

    IMDB_Record *meta = IMDB_RecordCreate(1024);
    CU_ASSERT(meta != NULL);
    IMDB_Metric *metric1 = IMDB_MetricCreate("metric1", "desc1", "type1");
    CU_ASSERT(metric1 != NULL);
    ret = IMDB_RecordAddMetric(meta, metric1);
    CU_ASSERT(ret == 0);
    IMDB_Metric *metric2 = IMDB_MetricCreate("metric2", "desc2", "type2");
    CU_ASSERT(metric2 != NULL);
    ret = IMDB_RecordAddMetric(meta, metric1);
    CU_ASSERT(ret == 0);

    ret = IMDB_TableSetMeta(table, meta);
    CU_ASSERT(ret == 0);

    ret = IMDB_DataBaseMgrAddTable(mgr, table);
    CU_ASSERT(ret == 0);

    char recordStr[] = "|table1|value1|value2|";
    ret = IMDB_DataBaseMgrAddRecord(mgr, recordStr, strlen(recordStr));
    CU_ASSERT(ret == 0);

    char buffer[2048] = {0};
    ret = IMDB_DataBaseMgrData2String(mgr, buffer, 2048);
    CU_ASSERT(ret == 0);
    printf("DatabaseMgr2String: \n");
    printf(buffer);

    IMDB_DataBaseMgrDestroy(mgr);
}

void TestIMDBMain(CU_pSuite suite)
{
    CU_ADD_TEST(suite, TestIMDB_MetricCreate);
    CU_ADD_TEST(suite, TestIMDB_MetricSetValue);
    CU_ADD_TEST(suite, TestIMDB_RecordCreate);
    CU_ADD_TEST(suite, TestIMDB_RecordAddMetric);
    CU_ADD_TEST(suite, TestIMDB_TableCreate);
    CU_ADD_TEST(suite, TestIMDB_TableSetMeta);
    CU_ADD_TEST(suite, TestIMDB_TableAddRecord);
    CU_ADD_TEST(suite, TestIMDB_DataBaseMgrCreate);
    CU_ADD_TEST(suite, TestIMDB_DataBaseMgrAddTable);
    CU_ADD_TEST(suite, TestIMDB_DataBaseMgrFindTable);
    CU_ADD_TEST(suite, TestIMDB_DataBaseMgrAddRecord);
    CU_ADD_TEST(suite, TestIMDB_DataBaseMgrData2String);
}

