#ifndef __PROBE_H__
#define __PROBE_H__

#include <stdint.h>
#include <pthread.h>

#define MAX_PROBE_NAME_LEN 256
#define MAX_META_PATH_LEN 4096
#define MAX_THREAD_NAME 128

#define MAX_PROBES_LIST_SIZE 2048

#define MACRO2STR1(MACRO) #MACRO
#define MACRO2STR2(MACRO) MACRO2STR1(MACRO)

typedef int (*probe_main)();

struct probe {
    char name[MAX_PROBE_NAME_LEN];
    char meta_path[MAX_META_PATH_LEN];

    probe_main func;
    pthread_t tid;
};

struct probe_mgr {
    uint32_t probes_num;
    struct probe probes[MAX_PROBES_LIST_SIZE];
};

struct probe_mgr *create_probe_mgr();
void destroy_probe_mgr(struct probe_mgr *probe_mgr);

int load_probes(struct probe_mgr *probe_mgr);
int run_probes(struct probe_mgr *probe_mgr);
int wait_probes_done(struct probe_mgr *probe_mgr);

#endif
