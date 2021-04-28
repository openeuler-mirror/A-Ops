#ifndef __DAEMON_H__
#define __DAEMON_H__

#include <stdint.h>
#include <stdio.h>

#include "resource.h"

uint32_t DaemonRun(ResourceMgr *mgr);
uint32_t DaemonWaitDone(ResourceMgr *mgr);

#endif

