#include <stdint.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include <dlfcn.h>
#include <sys/prctl.h>
#include <unistd.h>

#include "probe.h"

struct probe_mgr *create_probe_mgr()
{
    struct probe_mgr *mgr = NULL;
    mgr = (struct probe_mgr *)malloc(sizeof(struct probe_mgr));
    memset(mgr, 0, sizeof(struct probe_mgr));
    return mgr;
}

void destroy_probe_mgr(struct probe_mgr *probe_mgr)
{
    if (probe_mgr == NULL) {
        return;
    }
    free(probe_mgr);
    return;
}

int load_probes(struct probe_mgr *probe_mgr)
{
    int count = 0;
    char *p = NULL;

    char probes_list[] = MACRO2STR2(PROBES_LIST);
    char probes_meta_list[] = MACRO2STR2(PROBES_META_LIST);

    // get probe name
    count = 0;
    p = strtok(probes_list, " ");
    while (p != NULL) {
        memcpy(probe_mgr->probes[count].name, p, strlen(p));
        p = strtok(NULL, " ");
        count++;
    }

    // get probe meta path
    count = 0;
    p = strtok(probes_meta_list, " ");
    while (p != NULL) {
        memcpy(probe_mgr->probes[count].meta_path, p, strlen(p));
        p = strtok(NULL, " ");
        count++;
    }

    // get probe process func
    char probe_main_str[MAX_PROBE_NAME_LEN];
    void *hdl = dlopen(NULL, RTLD_NOW | RTLD_GLOBAL);
    if (hdl == NULL) {
        return -1;
    }

    probe_mgr->probes_num = count;
    printf("[GOPHER_DEBUG] get probes_num: %u\n", probe_mgr->probes_num);
    for (int i = 0; i < count; i++) {
        snprintf(probe_main_str, MAX_PROBE_NAME_LEN - 1, "probe_main_%s", probe_mgr->probes[i].name);
        probe_mgr->probes[i].func = dlsym(hdl, probe_main_str);
        if (probe_mgr->probes[i].func == NULL) {
            printf("[GOPHER_DEBUG] Unknown func: %s\n", probe_main_str);
            dlclose(hdl);
            return -1;
        }
    }

    dlclose(hdl);
    return 0;
}

static void *run_single_probe(void *arg)
{
    struct probe *probe = (struct probe *)arg;

    char thread_name[MAX_THREAD_NAME];
    snprintf(thread_name, MAX_THREAD_NAME - 1, "[PROBE]%s", probe->name);
    prctl(PR_SET_NAME, thread_name);

    for (;;) {
        probe->func();
        sleep(1);
    }
    return 0;
}

int run_probes(struct probe_mgr *probe_mgr)
{
    int ret = 0;
    for (int i = 0; i < probe_mgr->probes_num; i++) {
        ret = pthread_create(&probe_mgr->probes[i].tid, NULL, run_single_probe, &probe_mgr->probes[i]);
        if (ret != 0) {
            printf("[GOPHER_DEBUG] create probe thread failed. probe name: %s\n", probe_mgr->probes[i].name);
            return -1;
        }
        printf("[GOPHER_DEBUG] create %s probe thread success.\n", probe_mgr->probes[i].name);
        sleep(1);
    }
    return 0;
}

int wait_probes_done(struct probe_mgr *probe_mgr)
{
    for (int i = 0; i < probe_mgr->probes_num; i++) {
        pthread_join(probe_mgr->probes[i].tid, NULL);
    }
    return 0;
}
