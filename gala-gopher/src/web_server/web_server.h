#ifndef __WEB_SERVER_H__
#define __WEB_SERVER_H__

#include <stdint.h>
#include <semaphore.h>
#include <microhttpd.h>

#include "imdb.h"
#include "base.h"

typedef struct {
    uint16_t port;

    IMDB_DataBaseMgr *imdbMgr;
    struct MHD_Daemon *daemon;
} WebServer;

WebServer *WebServerCreate(uint16_t port);
void WebServerDestroy(WebServer *webServer);
int WebServerStartDaemon(WebServer *WebServer);

#endif

