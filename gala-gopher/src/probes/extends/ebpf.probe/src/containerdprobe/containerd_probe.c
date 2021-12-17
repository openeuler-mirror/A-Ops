#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/resource.h>
#ifdef BPF_PROG_KERN
#undef BPF_PROG_KERN
#endif

#ifdef BPF_PROG_USER
#undef BPF_PROG_USER
#endif

#include "bpf.h"
#include "containerd_probe.skel.h"
#include "containerd_probe.h"
#include "args.h"

#define METRIC_NAME_RUNC_TRACE    "container_data"
#define CONTAINERS_MAP_FILE_PATH  "/sys/fs/bpf/probe/containers"

static struct probe_params params = {.period = 5,
                                     .elf_path = {0}};
static volatile bool exiting = false;
static void sig_handler(int sig)
{
    exiting = true;
}

static void bpf_update_containerd_symaddrs(int fd)
{
    struct go_containerd_t symaddrs = {0};
    unsigned int pid = get_bin_process_id("containerd");

    bpf_map_lookup_elem(fd, &pid, &symaddrs);

    // Arguments of runtime/v1/linux.(*Task).Start.
    // https://github.com/containerd/containerd/blob/release/1.2/runtime/v1/linux/task.go#L120
    symaddrs.task_Start_t_offset            = 8;
    // Arguments of runtime/v1/linux.(*Task).Delete.
    // https://github.com/containerd/containerd/blob/release/1.2/runtime/v1/linux/task.go#L88
    symaddrs.task_Delete_t_offset           = 8;
    symaddrs.task_Delete_resp_offset        = 24;
    // Members of /runtime/v1/linux.Task
    // https://github.com/containerd/containerd/blob/release/1.2/runtime/v1/linux/task.go#L42
    symaddrs.linux_Task_id_offset           = 8;
    symaddrs.linux_Task_pid_offset          = 24;
    symaddrs.linux_Task_namespace_offset    = 40;
    symaddrs.linux_Task_cg_offset           = 56;
    // Members of /runtime.Exit
    // https://github.com/containerd/containerd/blob/release/1.2/runtime/runtime.go#L54
    symaddrs.runtime_Exit_Pid_offset        = 0;
    symaddrs.runtime_Exit_Status_offset     = 4;
    symaddrs.runtime_Exit_Timestamp_offset  = 8;

    bpf_map_update_elem(fd, &pid, &symaddrs, BPF_ANY);
}

static void print_container_metric(int fd)
{
    int ret = -1;
    struct container_key    k  = {0};
    struct container_key    nk = {0};
    struct container_value  v  = {0};

    char cid_str[CONTAINER_ID_LEN];
    char ns_str[NAMESPACE_LEN];

    while (bpf_map_get_next_key(fd, &k, &nk) != -1) {
        ret = bpf_map_lookup_elem(fd, &nk, &v);
        if (ret) {
            continue;
        }
        if (v.task_pid != 0) {
            fprintf(stdout, "|%s|%s|%s|%u|%u|\n",
                METRIC_NAME_RUNC_TRACE,
                nk.container_id,
                v.namespace,
                v.task_pid,
                v.status);
        }
        k = nk;
    }
    fflush(stdout);
    return;
}

int main(int argc, char **argv)
{
    int err = -1;
    char *elf[PATH_NUM] = {0};
    int elf_num = -1;
    int attach_flag = 0;

    err = args_parse(argc, argv, "t:p:", &params);
    if (err != 0) {
        return -1;
    }
    printf("arg parse interval time:%us\n", params.period);
    printf("arg parse input elf's path:%s\n", params.elf_path);

    LOAD(containerd_probe);

    /* Cleaner handling of Ctrl-C */
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    /* Update BPF symaddrs for this binary */
    bpf_update_containerd_symaddrs(GET_MAP_FD(containerd_symaddrs_map));

    /* Find elf's abs_path */
    ELF_REAL_PATH(containerd, params.elf_path, NULL, elf, elf_num);
    if (elf_num <= 0) {
        return -1;
    }

    /* Attach tracepoint handler for each elf_path */
    for (int i = 0; i < elf_num; i++) {
        int ret = 0;
        UBPF_ATTACH(linux_Task_Start, elf[i], github.com/containerd/containerd/runtime/v1/linux.(*Task).Start, ret);
        if (ret <= 0) {
            continue;
        }
        UBPF_ATTACH(linux_Task_Delete, elf[i], github.com/containerd/containerd/runtime/v1/linux.(*Task).Delete, ret);
        if (ret <= 0) {
            continue;
        }
        attach_flag = 1;
    }
    free_exec_path_buf(elf, elf_num);
    if (!attach_flag) {
        goto err;
    }

    int pinned = bpf_obj_pin(GET_MAP_FD(containers_map), CONTAINERS_MAP_FILE_PATH);
    if (pinned < 0) {
        printf("Failed to pin containers_map to the file system: %d (%s)\n", pinned, strerror(errno));
        goto err;
    }

    while (!exiting) {
        print_container_metric(GET_MAP_FD(containers_map));
        sleep(params.period);
    }

err:
/* Clean up */
    UNLOAD(containerd_probe);
    if (access(CONTAINERS_MAP_FILE_PATH, F_OK) == 0){
        if (remove(CONTAINERS_MAP_FILE_PATH) < 0) {
            printf("Delete the pinned file:%s failed!\n", CONTAINERS_MAP_FILE_PATH);
        }
    }
    return -err;
}
