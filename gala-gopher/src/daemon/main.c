/******************************************************************************
 * Copyright (c) Huawei Technologies Co., Ltd. 2021. All rights reserved.
 * gala-gopher licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Author: algorithmofdish
 * Create: 2021-09-28
 * Description: provide gala-gopher main functions
 ******************************************************************************/
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

