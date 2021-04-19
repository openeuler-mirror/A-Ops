#ifndef __PROBE_DATA_H__
#define __PROBE_DATA_H__

#include <stdint.h>

#define MAX_DATA_STR_LEN 1024

typedef struct {
    uint32_t dataLen;
    char data[MAX_DATA_STR_LEN];
} ProbeData;

ProbeData *ProbeDataAlloc(const char *dataStr);
void ProbeDataFree(ProbeData *data);

#endif


