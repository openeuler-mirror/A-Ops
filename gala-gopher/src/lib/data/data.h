#ifndef __DATA_H__
#define __DATA_H__

#include <stdint.h>
#include <list.h>

#include "base.h"

typedef struct {
    uint32_t fieldsSize;
    uint32_t fieldsNum;
    char **fieldsValue;
} Record;

typedef struct {
    char name[MAX_TABLE_NAME_LEN];

    uint32_t recordsSize;
    uint32_t recordsNum;
    
} Table;

typedef struct {
    
    
} DataMgr;





#endif

