#include <stdio.h>
#include <stdlib.h>
#include <bpf/libbpf.h>
#include "util.h"

struct perf_buffer* create_pref_buffer(int map_fd, perf_buffer_sample_fn cb)
{
	struct perf_buffer_opts pb_opts = {};
	struct perf_buffer *pb;
    int ret;
    
	pb_opts.sample_cb = cb;
	pb = perf_buffer__new(map_fd, 8, &pb_opts);
    if (pb == NULL){
		fprintf(stderr, "ERROR: perf buffer new failed\n");
		return NULL;
    }
	ret = libbpf_get_error(pb);
	if (ret) {
		fprintf(stderr, "ERROR: failed to setup perf_buffer: %d\n", ret);
		perf_buffer__free(pb);
        return NULL;
	}
    return pb;
}

void poll_pb(struct perf_buffer *pb, int timeout_ms)
{
    int ret;
    
	while ((ret = perf_buffer__poll(pb, timeout_ms)) >= 0) {
        ;
	}
    return;
}
