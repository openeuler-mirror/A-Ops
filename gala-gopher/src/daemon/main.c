#include <stdio.h>
#include <pthread.h>
#include "daemon.h"

int main()
{
    int ret = 0;
    ResourceMgr *resourceMgr = NULL;

    resourceMgr = ResourceMgrCreate();
    if (resourceMgr == NULL) {
        printf("[MAIN] create resource manager failed.\n");
        return 0;
    }

    ret = ResourceMgrInit(resourceMgr);
    if (ret != 0) {
        printf("[MAIN] ResourceMgrInit failed.\n");
        return 0;
    }

    ret = DaemonRun(resourceMgr);
    if (ret != 0) {
        printf("[MAIN] daemon run failed.\n");
        return 0;
    }

    ret = DaemonWaitDone(resourceMgr);
    if (ret != 0) {
        printf("[MAIN] daemon wait done failed.\n");
        return 0;
    }

    ResourceMgrDeinit(resourceMgr);
    ResourceMgrDestroy(resourceMgr);
    return 0;
}

