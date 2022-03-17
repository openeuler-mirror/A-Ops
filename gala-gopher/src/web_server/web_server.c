/******************************************************************************
 * Copyright (c) Huawei Technologies Co., Ltd. 2021. All rights reserved.
 * iSulad licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Author: Hubble_Zhu
 * Create: 2021-04-12
 * Description:
 ******************************************************************************/
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/eventfd.h>
#include "web_server.h"

#define MAX_WEBPAGE_BUFFER_SIZE (8 * 1024 * 64)     // 64 KB
char g_buffer[MAX_WEBPAGE_BUFFER_SIZE];

#if GALA_GOPHER_INFO("inner func")
static int WebRequestCallback(void *cls,
                              struct MHD_Connection *connection,
                              const char *url,
                              const char *method,
                              const char *version,
                              const char *upload_data,
                              const size_t *upload_data_size,
                              void **ptr);
#endif

static int WebRequestCallback(void *cls,
                              struct MHD_Connection *connection,
                              const char *url,
                              const char *method,
                              const char *version,
                              const char *upload_data,
                              const size_t *upload_data_size,
                              void **ptr)
{
    static int dummy;
    IMDB_DataBaseMgr *imdbMgr = (IMDB_DataBaseMgr *)cls;
    struct MHD_Response *response;
    int ret, buf_len;

    if (strcmp(method, "GET") != 0) {
        return MHD_NO;
    }

    if (*ptr != &dummy) {
        *ptr = &dummy;
        return MHD_YES;
    }
    *ptr = NULL;

    if (*upload_data_size != 0) {
        return MHD_NO;
    }

    ret = IMDB_DataBaseMgrData2String(imdbMgr, g_buffer, MAX_WEBPAGE_BUFFER_SIZE, &buf_len);
    if (ret < 0) {
        return MHD_NO;
    }
    response = MHD_create_response_from_buffer(buf_len, (void *)g_buffer, MHD_RESPMEM_PERSISTENT);
    if (response == NULL) {
        return MHD_NO;
    }

    ret = MHD_add_response_header(response, MHD_HTTP_HEADER_CONTENT_TYPE, "text/plain");
    if (ret == MHD_NO) {
        MHD_destroy_response(response);
        return MHD_NO;
    }

    ret = MHD_queue_response(connection, MHD_HTTP_OK, response);
    if (ret != MHD_YES) {
        MHD_destroy_response(response);
        return MHD_NO;
    }

    MHD_destroy_response(response);
    return ret;
}

WebServer *WebServerCreate(uint16_t port)
{
    WebServer *server = NULL;
    server = (WebServer *)malloc(sizeof(WebServer));
    if (server == NULL) {
        return NULL;
    }
    memset(server, 0, sizeof(WebServer));

    server->port = port;
    return server;
}

void WebServerDestroy(WebServer *webServer)
{
    if (webServer == NULL) {
        return;
    }

    if (webServer->daemon != NULL) {
        MHD_stop_daemon(webServer->daemon);
    }

    free(webServer);
    return;
}

int WebServerStartDaemon(WebServer *webServer)
{
    webServer->daemon = MHD_start_daemon(MHD_USE_INTERNAL_POLLING_THREAD,
                                         webServer->port,
                                         NULL,
                                         NULL,
                                         &WebRequestCallback,
                                         webServer->imdbMgr,
                                         MHD_OPTION_END);
    if (webServer->daemon == NULL) {
        return -1;
    }

    return 0;
}

