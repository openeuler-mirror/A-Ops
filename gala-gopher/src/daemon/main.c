#include <stdio.h>
#include <pthread.h>
#include "daemon.h"

int main()
{
    uint32_t ret = 0;

    ResourceMgr *mgr = NULL;

    mgr = ResourceMgrCreate();
    if (mgr == NULL) {
        printf("[MAIN] create resource manager failed.\n");
        return 0;
    }

    ret = DaemonInit(mgr);
    if (ret != 0) {
        printf("[MAIN] daemon init failed.\n");
        return 0;
    }

    ret = DaemonRun(mgr);
    if (ret != 0) {
        printf("[MAIN] daemon run failed.\n");
        return 0;
    }

    ret = DaemonWaitDone(mgr);
    if (ret != 0) {
        printf("[MAIN] daemon wait done failed.\n");
        return 0;
    }

    return 0;
}

