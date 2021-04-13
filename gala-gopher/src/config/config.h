#ifndef __CONFIG_H__
#define __CONFIG_H__

#include <stdint.h>

struct gopher_cfg {
    uint32_t pad;
};

struct gopher_cfg *create_cfg_mgr();
void destroy_cfg_mgr(struct gopher_cfg *cfg_mgr);

#endif
