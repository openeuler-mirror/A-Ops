#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include "probe_data.h"


ProbeData *ProbeDataAlloc(const char *dataStr)
{
    ProbeData *data = NULL;
    uint32_t memorySize = sizeof(uint32_t) + strlen(dataStr);
    
    data = (ProbeData *)malloc(memorySize);
    if (data == NULL) {
        return NULL;
    }

    memset(data, 0, memorySize);
    data->dataLen = strlen(dataStr);
    memcpy(data + sizeof(uint32_t), dataStr, data->dataLen);

    return data;
}

void ProbeDataFree(ProbeData *data)
{
    if (data == NULL) {
        return;
    }

    free(data);
    return;
}



