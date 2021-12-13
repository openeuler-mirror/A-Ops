#include <stdio.h>
#include <stdlib.h>
#include <bpf/libbpf.h>
#include "container.h"

#define ERR_MSG "No such file or directory"
#define ERR_MSG2 "not installe"
#define RUNNING "active (running)"
#define MERGED_DIR "MergedDir"

#define DOCKER "/usr/bin/docker"
#define ISULAD "/usr/bin/isulad"

#define DOCKER_PS_COMMAND "ps | awk 'NR > 1 {print $1}'"
#define DOCKER_PID_COMMAND "--format '{{.State.Pid}}'"
#define DOCKER_COMM_COMMAND "/usr/bin/cat /proc/%u/comm"
#define DOCKER_POD_COMMAND "--format '{{.Config.Labels}}' | awk -F 'io.kubernetes.pod.name:' '{print $2}' | awk '{print $1}'"
#define DOCKER_NETNS_COMMAND "/usr/bin/ls -l /proc/%u/ns/net | awk -F '[' '{print $2}' | awk -F ']' '{print $1}'"
#define DOCKER_CGP_COMMAND "/usr/bin/ls -l /proc/%u/ns/cgroup | awk -F '[' '{print $2}' | awk -F ']' '{print $1}'"
#define DOCKER_MNTNS_COMMAND "/usr/bin/ls -l /proc/%u/ns/mnt | awk -F '[' '{print $2}' | awk -F ']' '{print $1}'"
#define DOCKER_INSPECT_COMMAND "inspect"
#define DOCKER_MERGED_COMMAND "MergedDir | awk -F '\"' '{print $4}'"

#define LEN_BUF 256
#define COMMAND_LEN 512

#define __SPLIT_NEWLINE_SYMBOL(s) \
    do { \
        int __len = strlen(s); \
        if (__len > 0 && s[__len - 1] == '\n') { \
            s[__len - 1] = 0; \
        } \
    } while(0) \

bool __is_install_rpm(const char* command){
    char line[LEN_BUF];
    FILE *f;
    bool is_installed;

    is_installed = false;
    f = popen(command, "r");
    if (f == NULL) {
        return false;
    }
    (void)memset(line, 0, LEN_BUF);
    if (NULL == fgets(line, LEN_BUF, f)) {
        goto out;
    }

    if (strstr(line, ERR_MSG2) != NULL) {
        goto out;            
    }
    is_installed = true;
out:
    (void)pclose(f);
    return is_installed;
}

bool __is_service_running(const char* service){
    char line[LEN_BUF];
    FILE *f;
    bool is_running;

    is_running = false;
    f = popen(service, "r");
    if (f == NULL) {
        return false;
    }
    
    while (!feof(f)) {
        (void)memset(line, 0, LEN_BUF);
        if (NULL == fgets(line, LEN_BUF, f)) {
            goto out;
        }

        if (strstr(line, RUNNING) != NULL) {
            is_running = true;
            goto out;            
        }
    }
    
out:
    (void)pclose(f);
    return is_running;
}

bool __is_dockerd(){
    if(__is_install_rpm("/usr/bin/rpm -ql docker-engine")) {
        return __is_service_running("/usr/bin/systemctl status docker");
    }
}

bool __is_isulad(){
    if(__is_install_rpm("/usr/bin/rpm -ql iSulad")) {
        return __is_service_running("/usr/bin/systemctl service iSulad");
    }
}

int __get_container_count(const char *command_s) {
    int container_num;
    char line[LEN_BUF];
    char command[COMMAND_LEN];
    FILE *f;

    container_num = 0;
    (void)memset(command, 0, COMMAND_LEN);
    (void)snprintf(command, COMMAND_LEN, "%s %s", command_s, DOCKER_PS_COMMAND);
    f = popen(command, "r");
    if (f == NULL) {
        return 0;
    }

    while (!feof(f)) {
        (void)memset(line, 0, LEN_BUF);
        if (NULL == fgets(line, LEN_BUF, f)) {
            goto out;
        }

        if (strstr(line, ERR_MSG) != NULL) {
            goto out;            
        }

        container_num++;
    }

out:
    (void)pclose(f);
    return container_num;
}

int __get_containers_id(container_tbl* cstbl, const char *command_s) {
    char line[LEN_BUF];
    FILE *f;
    int index, ret;
    container_info *p;
    char command[COMMAND_LEN];

    p = cstbl->cs;
    index = 0;
    (void)memset(command, 0, COMMAND_LEN);
    (void)snprintf(command, COMMAND_LEN, "%s %s", command_s, DOCKER_PS_COMMAND);
    f = popen(command, "r");
    if (f == NULL) {
        return -1;
    }

    ret = 0;
    while (!feof(f) && index < cstbl->num) {
        (void)memset(line, 0, LEN_BUF);
        if (NULL == fgets(line, LEN_BUF, f)) {
            ret = -1;
            goto out;
        }
        __SPLIT_NEWLINE_SYMBOL(line);
        (void)snprintf(p->container, CONTAINER_ID_LEN, "%s", line);
        p++;
        index++;
    }

out:
    (void)pclose(f);
    return ret;
}

int __get_containers_pid(container_tbl* cstbl, const char *command_s) {    
    char line[LEN_BUF];
    char command[COMMAND_LEN];
    FILE *f;
    int index;
    container_info *p;

    p = cstbl->cs;
    index = 0;
    for (index = 0; index < cstbl->num; index++) {
        (void)memset(command, 0, COMMAND_LEN);
        (void)snprintf(command, COMMAND_LEN, "%s inspect %s %s", 
                command_s, p->container, DOCKER_PID_COMMAND);
        f = NULL;
        f = popen(command, "r");
        if (f == NULL) {
            continue;
        }
        (void)memset(line, 0, LEN_BUF);
        if (NULL == fgets(line, LEN_BUF, f)) {
            (void)pclose(f);
            continue;
        }
        __SPLIT_NEWLINE_SYMBOL(line);
        p->pid = (unsigned int)atoi((const char *)line);
        p++;
        (void)pclose(f);
    }
    return 0;
}

int __get_containers_comm(container_tbl* cstbl, const char *command_s) {    
    char line[LEN_BUF];
    char command[COMMAND_LEN];
    FILE *f;
    int index;
    container_info *p;

    p = cstbl->cs;
    index = 0;
    (void)command_s;
    for (index = 0; index < cstbl->num; index++) {
        (void)memset(command, 0, COMMAND_LEN);
        (void)snprintf(command, COMMAND_LEN, DOCKER_COMM_COMMAND, p->pid);
        f = NULL;
        f = popen(command, "r");
        if (f == NULL) {
            continue;
        }
        (void)memset(line, 0, LEN_BUF);
        if (NULL == fgets(line, LEN_BUF, f)) {
            (void)pclose(f);
            continue;
        }
        __SPLIT_NEWLINE_SYMBOL(line);
        (void)snprintf(p->comm, COMM_LEN, "%s", line);
        p++;
        (void)pclose(f);
    }
    return 0;
}

int __get_containers_pod(container_tbl* cstbl, const char *command_s) {
    char line[LEN_BUF];
    char command[COMMAND_LEN];
    FILE *f;
    int index;
    container_info *p;

    p = cstbl->cs;
    index = 0;
    (void)command_s;
    for (index = 0; index < cstbl->num; index++) {
        (void)memset(command, 0, COMMAND_LEN);
        (void)snprintf(command, COMMAND_LEN, "%s inspect %s %s", 
                    command_s, p->container, DOCKER_POD_COMMAND);
        f = NULL;
        f = popen(command, "r");
        if (f == NULL) {
            continue;
        }
        (void)memset(line, 0, LEN_BUF);
        if (NULL == fgets(line, LEN_BUF, f)) {
            (void)pclose(f);
            continue;
        }
        __SPLIT_NEWLINE_SYMBOL(line);
        (void)snprintf(p->pod, POD_NAME_LEN, "%s", line);
        p++;
        (void)pclose(f);
    }
    return 0;
}

unsigned int __get_pid_namespace(unsigned int pid, const char *namespace) {
    char line[LEN_BUF];
    char command[COMMAND_LEN];
    FILE *f;

    (void)memset(command, 0, COMMAND_LEN);
    (void)snprintf(command, COMMAND_LEN, namespace, pid);
    f = popen(command, "r");
    if (f == NULL) {
        return -1;
    }
    (void)memset(line, 0, LEN_BUF);
    if (NULL == fgets(line, LEN_BUF, f)) {
        (void)pclose(f);
        return -1;
    }
    (void)pclose(f);
    __SPLIT_NEWLINE_SYMBOL(line);
    return (unsigned int)strtoul((const char *)line, NULL, 10);
}

int __get_containers_netns(container_tbl* cstbl, const char *command_s) {
    int index;
    unsigned int netns;
    container_info *p;

    p = cstbl->cs;
    index = 0;
    (void)command_s;
    for (index = 0; index < cstbl->num; index++) {
        netns = __get_pid_namespace(p->pid, DOCKER_NETNS_COMMAND);
        if (netns > 0) {
            p->netns = netns;
        }
        p++;
    }
    return 0;
}

int __get_containers_mntns(container_tbl* cstbl, const char *command_s) {
    int index;
    unsigned int mntns;
    container_info *p;

    p = cstbl->cs;
    index = 0;
    (void)command_s;
    for (index = 0; index < cstbl->num; index++) {
        mntns = __get_pid_namespace(p->pid, DOCKER_MNTNS_COMMAND);
        if (mntns > 0) {
            p->mntns = mntns;
        }
        p++;
    }
    return 0;
}

int __get_containers_cgroup(container_tbl* cstbl, const char *command_s) {
    int index;
    unsigned int cgroup;
    container_info *p;

    p = cstbl->cs;
    index = 0;
    (void)command_s;
    for (index = 0; index < cstbl->num; index++) {
        cgroup = __get_pid_namespace(p->pid, DOCKER_CGP_COMMAND);
        if (cgroup > 0) {
            p->cgroup = cgroup;
        }
        p++;
    }
    return 0;
}

container_tbl* __get_all_container(const char *command_s) {

    int container_num;
    size_t size;
    container_tbl *cstbl;

    cstbl = NULL;
    container_num = __get_container_count(command_s);
    if (container_num <= 0) {
        goto out;
    }

    size = sizeof(container_tbl) + container_num * sizeof(container_info);
    cstbl = (container_tbl *)malloc(size);
    if (cstbl == NULL) {
        goto out;
    }

    cstbl->num = container_num;
    cstbl->cs = (container_info *)(cstbl + 1);

    if (__get_containers_id(cstbl, command_s) < 0) {
        (void)free(cstbl);
        cstbl = NULL;
        goto out;
    }
    (void)__get_containers_pid(cstbl, command_s);
    (void)__get_containers_comm(cstbl, command_s);
    (void)__get_containers_netns(cstbl, command_s);
    (void)__get_containers_cgroup(cstbl, command_s);
    (void)__get_containers_mntns(cstbl, command_s);
    (void)__get_containers_pod(cstbl, command_s);
out:
    return cstbl;
}

container_tbl* get_all_container() {
    bool is_docker, is_isula;
    
    is_docker = __is_dockerd();
    is_isula = __is_isulad();

    if (is_docker) {
        return __get_all_container(DOCKER);
    }

    if (is_isula) {
        return __get_all_container(ISULAD);
    }
    return 0;
}

const char* get_container_id_by_pid(container_tbl* cstbl, unsigned int pid) {
    int i;
    unsigned int cgroup, mntns, netns;
    container_info *p = cstbl->cs;
    
    cgroup = __get_pid_namespace(pid, DOCKER_CGP_COMMAND);
    mntns = __get_pid_namespace(pid, DOCKER_MNTNS_COMMAND);
    netns = __get_pid_namespace(pid, DOCKER_NETNS_COMMAND);

    for (i = 0; i < cstbl->num; i++) {
        if ((mntns > 0) && (p->mntns == (unsigned int)mntns)) {
            return (const char*)p->container;
        }
        if ((cgroup > 0) && (p->cgroup == (unsigned int)cgroup)) {
            return (const char*)p->container;
        }
        if ((netns > 0) && (p->netns == (unsigned int)netns)) {
            return (const char*)p->container;
        }
        p++;
    }
    return NULL;
}

void free_container_tbl(container_tbl **pcstbl) {
    free(*pcstbl);
    *pcstbl = NULL;
}

/*
parse string
[root@node2 ~]# docker inspect 92a7a60249cb | grep MergedDir | awk -F '"' '{print $4}' 
                /var/lib/docker/overlay2/82c62b73874d9a17a78958d5e13af478b1185db6fa614a72e0871c1b7cd107f5/merged
*/
int get_container_merged_path(const char *container_id, char *path, unsigned int len) {
    FILE *f;
    char command[COMMAND_LEN];

    command[0] = 0;
    path[0] = 0;
    if (__is_dockerd()) {
        (void)snprintf(command, COMMAND_LEN, "%s %s %s | grep %s", \
            DOCKER, DOCKER_INSPECT_COMMAND, container_id, DOCKER_MERGED_COMMAND);
    } else if (__is_isulad()) {
        (void)snprintf(command, COMMAND_LEN, "%s %s %s | grep %s", \
            ISULAD, DOCKER_INSPECT_COMMAND, container_id, DOCKER_MERGED_COMMAND);
    } else {
        return -1;
    }

    f = popen(command, "r");
    if (f == NULL) {
        return -1;
    }

    if (NULL == fgets(path, len, f)) {
        (void)pclose(f);
        return -1;
    }
    __SPLIT_NEWLINE_SYMBOL(path);
    (void)pclose(f);
    return 0;
}

/* docker exec -it 92a7a60249cb [xxx] */
int exec_container_command(const char *container_id, const char *exec, char *buf, unsigned int len) {
    FILE *f;
    char command[COMMAND_LEN];

    command[0] = 0;
    buf[0] = 0;
    if (__is_dockerd()) {
        (void)snprintf(command, COMMAND_LEN, "%s exec -it %s %s", \
            DOCKER, container_id, exec);
    } else if (__is_isulad()) {
        (void)snprintf(command, COMMAND_LEN, "%s exec -it %s %s", \
            ISULAD, container_id, exec);
    } else {
        return -1;
    }

    f = popen(command, "r");
    if (f == NULL) {
        return -1;
    }

    if (NULL == fgets(buf, len, f)) {
        (void)pclose(f);
        return -1;
    }
    __SPLIT_NEWLINE_SYMBOL(buf);
    (void)pclose(f);
    return 0;
}


