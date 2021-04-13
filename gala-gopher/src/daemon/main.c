#include <stdio.h>

#include "probe.h"

int main()
{
    int ret = 0;

    struct probe_mgr *probe_mgr;
    probe_mgr = create_probe_mgr();
    if (probe_mgr == NULL) {
        printf("[GOPHER_DEBUG] create probe mgr failed.\n");
        return 0;
    }

    ret = load_probes(probe_mgr);
    if (ret != 0) {
        printf("[GOPHER_DEBUG] load probe mgr failed.\n");
        return 0;
    }

    ret = run_probes(probe_mgr);
    if (ret != 0) {
        printf("[GOPHER_DEBUG] start probes failed.\n");
        return 0;
    }
    printf("[GOPHER DEBUG] process start success.\n");

    wait_probes_done(probe_mgr);
    destroy_probe_mgr(probe_mgr);

    return 0;
}
