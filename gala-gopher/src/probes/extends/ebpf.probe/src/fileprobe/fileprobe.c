#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/resource.h>
#include <bpf/libbpf.h>

#include "fileprobe.skel.h"
#include "fileprobe.h"

#define PROBE_NAME "file_snoop"
#define FILE_TO_INODE "/usr/bin/ls -i %s | awk '{print $1}'"
#define INODE_TO_FILE "/usr/bin/find / -inum %u"

struct snoop_file sf[] = {
    {"/etc/passwd", "/usr/bin/vim", OP_TYPE_WRITE},
};

static int libbpf_print_fn(enum libbpf_print_level level, const char *format, va_list args)
{
    if (level == LIBBPF_WARN)
        return vfprintf(stderr, format, args);

    return 0;
}

static volatile sig_atomic_t stop;

static void sig_int(int signo)
{
    stop = 1;
}

static void bump_memlock_rlimit(void)
{
    struct rlimit rlim_new = {
        .rlim_cur = RLIM_INFINITY,
        .rlim_max = RLIM_INFINITY,
    };

    if (setrlimit(RLIMIT_MEMLOCK, &rlim_new)) {
        fprintf(stderr, "Failed to increase RLIMIT_MEMLOCK limit!\n");
        exit(1);
    }
}

int get_file_name(const u32 inode, char *file_name, u32 max_len) {
    char command[64];
    char line[FILE_NAME_LEN];
    FILE *f = NULL;

    // init
    command[0] = 0; 
    line[0] = 0;
    
    if (snprintf(command, 64, INODE_TO_FILE, inode) < 0) {
        return -1;
    }
    f = popen(command, "r");
    if (!f) {
        return -1;
    }

    if (fgets(line, FILE_NAME_LEN, f) == NULL) {
        pclose(f);
        return -1;
    }

    pclose(f);
    if (snprintf(file_name, max_len, line) < 0) {
        return -1;
    }
    return 0;
}


void read_probe_data(int map_fd)
{
    struct snoop_evt evt;
    char file_name[FILE_NAME_LEN];
    struct suspicious_op_key key = {0};
    struct suspicious_op_key next_key;
    struct suspicious_op_val v;

    while (bpf_map_get_next_key(map_fd, &key, &next_key) != -1) {
        if (bpf_map_lookup_elem(map_fd, &next_key, &v) != 0) {
            continue;
        }

        file_name[0] = 0;
        if (get_file_name((const u32)next_key.inode, file_name, FILE_NAME_LEN) != 0) {
            continue;
        }
        evt.op_type = v.op_type;
        evt.ts = next_key.ts;
        evt.exe[0] = 0;
        if (snprintf(evt.exe, FILE_NAME_LEN, v.exe) < 0) {
            continue;
        }
        evt.file[0] = 0;
        if (snprintf(evt.file, FILE_NAME_LEN, file_name) < 0) {
            continue;
        }
        fprintf(stdout,
            "|%s|%llu|%u|%s|%s|\n",
            PROBE_NAME,
            evt.ts,
            evt.op_type,
            evt.exe,
            evt.file);
        bpf_map_delete_elem(map_fd, &next_key);
    }
    return;
}

void run(struct fileprobe_bpf *skel)
{
    if (signal(SIGINT, sig_int) == SIG_ERR) {
        fprintf(stderr, "can't set signal handler: %s\n", strerror(errno));
        return;
    }

    while (!stop) {
        read_probe_data(bpf_map__fd(skel->maps.suspicious_op_map));
        sleep(PROBE_CYCLE_SEC);
    }
    return;
}


struct fileprobe_bpf* load_and_attach_progs()
{
    struct fileprobe_bpf *skel;
    int err;
    
    /* Set up libbpf errors and debug info callback */
    libbpf_set_print(libbpf_print_fn);

    /* Bump RLIMIT_MEMLOCK to allow BPF sub-system to do anything */
    bump_memlock_rlimit();

    /* Open load and verify BPF application */
    skel = fileprobe_bpf__open_and_load();
    if (!skel) {
        fprintf(stderr, "Failed to open fileprobe BPF skeleton\n");
        return NULL;
    }

    /* Attach tracepoint handler */
    err = fileprobe_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "Failed to attach fileprobe BPF skeleton\n");
        fileprobe_bpf__destroy(skel);
        return NULL;
    }
    
    return skel;
}


bool is_valid_file(const char* file_name) {
    if (access(file_name, 0) == 0) {
        return true;
    }
    return false;
}

bool is_executable_file(const char* exe) {
    if (access(exe, 1) == 0) {
        return true;
    }
    return false;
}

int get_file_inode_id(const char* file_name, u32 *i_inode) {
    char command[512];
    char line[32];
    FILE *f = NULL;

    // init
    command[0] = 0; 
    line[0] = 0;
    
    if (snprintf(command, 512, FILE_TO_INODE, file_name) < 0) {
        return -1;
    }
    f = popen(command, "r");
    if (!f) {
        return -1;
    }

    if (fgets(line, 32, f) == NULL) {
        pclose(f);
        return -1;
    }

    *i_inode = (u32)atoi(line);
    pclose(f);
    return 0;
}


int update_snoop_files(const char* file_name, int map_fd) {
    u32 i_inode;
    u32 v = 0;
    struct snoop_inode s_inode;
    
    if (!is_valid_file(file_name)) {
        return -1;
    }

    if (get_file_inode_id(file_name, &i_inode) < 0) {
        return -1;
    }

    s_inode.inode = (unsigned long)i_inode;
    
    return bpf_map_update_elem(map_fd, &s_inode, &v, BPF_ANY);
}


int update_permissions(const char* file_name, const char* exe, u32 permission, int map_fd) {
    u32 i_inode;
    struct snoop_inode s_inode;
    struct inode_permissions inode_permission;

    inode_permission.permission = permission;
    if (snprintf(inode_permission.exe, FILE_NAME_LEN, exe) < 0) {
        return -1;
    }
    
    if (!is_executable_file(exe)) {
        return -1;
    }

    if (!is_valid_file(file_name)) {
        return -1;
    }

    if (get_file_inode_id(file_name, &i_inode) < 0) {
        return -1;
    }

    s_inode.inode = (unsigned long)i_inode;
    
    return bpf_map_update_elem(map_fd, &s_inode, &inode_permission, BPF_ANY);
}


int main(int argc, char **argv)
{
    struct fileprobe_bpf *skel;

    skel = load_and_attach_progs();
    if (!skel) {
        return -1;
    }

    if (update_snoop_files((const char *)sf[0].file, 
                bpf_map__fd(skel->maps.snoop_files_map)) < 0) {
        goto err;
    }

    if (update_permissions((const char *)sf[0].file, 
                (const char *)sf[0].exe,
                sf[0].permission,
                bpf_map__fd(skel->maps.permissions_map)) < 0) {
        goto err;
    }
    
    run(skel);

err:
    fileprobe_bpf__destroy(skel);
    return 0;
}
