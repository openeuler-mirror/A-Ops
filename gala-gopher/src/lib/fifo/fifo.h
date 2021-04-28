#ifndef __FIFO_H__
#define __FIFO_H__

#include <stdint.h>

typedef struct {
    void **buffer;
    uint32_t size;
    uint32_t in;
    uint32_t out;

    int triggerFd;
} Fifo;

typedef struct {
    uint32_t size;
    uint32_t fifoNum;
    Fifo **fifos;
} FifoMgr;

Fifo *FifoCreate(uint32_t size);
void FifoDestroy(Fifo *fifo);

uint32_t FifoPut(Fifo *fifo, void *element);
uint32_t FifoGet(Fifo *fifo, void **elements);

FifoMgr *FifoMgrCreate(int size);
void FifoMgrDestroy(FifoMgr *mgr);
int FifoMgrAdd(FifoMgr *mgr, Fifo *fifo);

#endif

