#ifndef __DAEMON_H__
#define __DAEMON_H__

#include <stdint.h>
#include <stdio.h>

#include "resource.h"

int DaemonRun(ResourceMgr *mgr);
int DaemonWaitDone(ResourceMgr *mgr);

#endif

