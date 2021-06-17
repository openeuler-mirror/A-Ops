#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/resource.h>
#include <bpf/libbpf.h>

#include "killprobe.skel.h"
#include "killprobe.h"
#include "util.h"

#define PROBE_NAME "kill_info"

static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args)
{
    if (level == LIBBPF_WARN)
        return vfprintf(stderr, format, args);

    return 0;
}

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


struct killprobe_bpf* load_and_attach_progs()
{
    struct killprobe_bpf *skel;
    int err;
    
    /* Set up libbpf errors and debug info callback */
    libbpf_set_print(libbpf_print_fn);

	#if UNIT_TESTING
    /* Bump RLIMIT_MEMLOCK  allow BPF sub-system to do anything */
    if (set_memlock_rlimit() == 0) {
		return NULL;
	}
	#endif

    /* Open load and verify BPF application */
    skel = killprobe_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Failed to open killprobe BPF skeleton\n");
        return NULL;
    }

    /* Attach tracepoint handler */
    err = killprobe_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "Failed to attach killprobe BPF skeleton\n");
        goto err;
    }
    
    return skel;
err:
    killprobe_bpf__destroy(skel);
    return NULL;
}


int main(int argc, char **argv)
{
    int map_fd;
    struct killprobe_bpf *skel;
    struct perf_buffer* pb;

    skel = load_and_attach_progs();
    if (!skel) {
        return -1;
    }

	map_fd = bpf_map__fd(skel->maps.output);
	if (map_fd < 0) {
		fprintf(stderr, "ERROR: finding a map in obj file failed\n");
		goto out;
	}

    pb = create_pref_buffer(map_fd, print_bpf_output);
    if (!pb) {
        fprintf(stderr, "ERROR: crate perf buffer failed\n");
        goto out;
    }

    poll_pb(pb, 1000);

    perf_buffer__free(pb);
out:    
    killprobe_bpf__destroy(skel);
    return 0;
}
