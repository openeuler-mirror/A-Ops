#include <stdint.h>
#include <CUnit/Basic.h>

#include "fifo.h"
#include "test_fifo.h"

#define FIFO_MGR_SIZE 1024
#define FIFO_SIZE  1024

void TestFifoMgrCreate()
{
    FifoMgr *mgr = FifoMgrCreate(FIFO_MGR_SIZE);

    CU_ASSERT(mgr != NULL);
    CU_ASSERT(mgr->fifos != NULL);
    CU_ASSERT(mgr->size == FIFO_MGR_SIZE);
    CU_ASSERT(mgr->fifoNum == 0);
    FifoMgrDestroy(mgr);
}

void TestFifoMgrAdd()
{
    uint32_t ret = 0;
    FifoMgr *mgr = FifoMgrCreate(FIFO_MGR_SIZE);
    Fifo *fifo = FifoCreate(FIFO_SIZE);

    ret = FifoMgrAdd(mgr, fifo);
    CU_ASSERT(ret == 0);
    CU_ASSERT(mgr->fifoNum == 1);
    CU_ASSERT(mgr->fifos[0] == fifo);
    FifoDestroy(fifo);
    FifoMgrDestroy(mgr);
}

void TestFifoCreate()
{
    Fifo *fifo = FifoCreate(FIFO_SIZE);

    CU_ASSERT(fifo != NULL);
    CU_ASSERT(fifo->buffer != NULL);
    CU_ASSERT(fifo->in == 0);
    CU_ASSERT(fifo->out == 0);
    CU_ASSERT(fifo->size == FIFO_SIZE);
    FifoDestroy(fifo);
}

void TestFifoPut()
{
    uint32_t ret = 0;
    uint32_t elem = 1;
    Fifo *fifo = FifoCreate(FIFO_SIZE);

    CU_ASSERT(fifo != NULL);
    ret = FifoPut(fifo, &elem);
    CU_ASSERT(ret == 0);
    CU_ASSERT(fifo->in == 1);
    FifoDestroy(fifo);
}

void TestFifoGet()
{
    uint32_t ret = 0;
    uint32_t elem = 1;
    uint32_t *elemP = NULL;
    Fifo *fifo = FifoCreate(FIFO_SIZE);

    CU_ASSERT(fifo != NULL);
    ret = FifoPut(fifo, &elem);
    CU_ASSERT(ret == 0);
    ret = FifoGet(fifo, (void **) &elemP);
    CU_ASSERT(ret == 0);
    CU_ASSERT(fifo->out == 1);
    FifoDestroy(fifo);
}

void TestFifoMain(CU_pSuite suite)
{
    CU_ADD_TEST(suite, TestFifoMgrCreate);
    CU_ADD_TEST(suite, TestFifoMgrAdd);
    CU_ADD_TEST(suite, TestFifoCreate);
    CU_ADD_TEST(suite, TestFifoPut);
    CU_ADD_TEST(suite, TestFifoGet);
}

