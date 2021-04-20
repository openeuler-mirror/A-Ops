#include <stdio.h>
#include <pthread.h>
#include "config.h"
#include "daemon.h"

int main()
{
    uint32_t ret = 0;
    ConfigMgr *configMgr = NULL;
    ResourceMgr *resourceMgr = NULL;

    configMgr = ConfigMgrCreate();
    if (configMgr == NULL) {
        printf("[MAIN] create config mgr failed.\n");
        return 0;
    }

    ret = ConfigMgrLoad(configMgr, GALA_CONF_PATH);
    if (ret != 0) {
        printf("[MAIN] load gala configuration failed.\n");
        return -1;
    }
    printf("[MAIN] load gala configuration success.\n");

    resourceMgr = ResourceMgrCreate(configMgr);
    if (resourceMgr == NULL) {
        printf("[MAIN] create resource manager failed.\n");
        return 0;
    }

    ret = DaemonInit(resourceMgr, configMgr);
    if (ret != 0) {
        printf("[MAIN] daemon init failed.\n");
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

    ResourceMgrDestroy(resourceMgr);
    ConfigMgrDestroy(configMgr);
    return 0;
}

