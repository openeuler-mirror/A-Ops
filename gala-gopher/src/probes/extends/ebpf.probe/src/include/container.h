#ifndef __CONTAINER_H__
#define __CONTAINER_H__

#define CONTAINER_ID_LEN    64
#define POD_NAME_LEN        64
#define COMM_LEN            64

typedef struct container_info_s {
    unsigned int pid;
    unsigned int netns;
    unsigned int mntns;
    unsigned int cgroup;
    char container[CONTAINER_ID_LEN];
    char pod[POD_NAME_LEN];
    char comm[COMM_LEN];
} container_info;

typedef struct container_tbl_s {
    unsigned int num;
    container_info *cs;
} container_tbl;

container_tbl* get_all_container();
const char* get_container_id_by_pid(container_tbl* cstbl, unsigned int pid);
void free_container_tbl(container_tbl **pcstbl);
#endif
