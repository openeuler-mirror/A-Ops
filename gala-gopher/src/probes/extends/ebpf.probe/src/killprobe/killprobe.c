#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/resource.h>


#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif

#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif

#include "bpf.h"
#include "args.h"

#include "killprobe.skel.h"
#include "killprobe.h"

#define PROBE_NAME "kill_info"

static struct probe_params params = {.period = 5};

static void print_bpf_output(void *ctx, int cpu, void *data, __u32 size)
{
    struct val_t *pv;

    pv = (struct val_t *)data;

    fprintf(stdout,
        "|%s|%llu|%u|%u|%s|\n",
        PROBE_NAME,
        pv->killer_pid,
        pv->signal,
        pv->killed_pid,
        pv->comm);
}


int main(int argc, char **argv)
{
    int map_fd, err;
    struct perf_buffer* pb;

    err = args_parse(argc, argv, "t:", &params);
    if (err != 0) {
        return -1;
    }
	
    printf("arg parse interval time:%us\n", params.period);

	LOAD(killprobe);

	map_fd = GET_MAP_FD(output);

    pb = create_pref_buffer(map_fd, print_bpf_output);
    if (!pb) {
        fprintf(stderr, "ERROR: crate perf buffer failed\n");
        goto err;
    }

    poll_pb(pb, params.period * 1000);

    perf_buffer__free(pb);
err:    
    UNLOAD(killprobe);
    return 0;
}
