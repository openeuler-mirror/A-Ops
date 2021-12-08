#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <unistd.h>
#include "container.h"

#define LEN_BUF 256
#define COMMAND_LEN 512
#define PATH_LEN 512

#define COMMAND_GLIBC_PATH \
    "/usr/bin/ldd /bin/ls | grep \"libc.so\" | awk -F '=>' '{print $2}' | awk '{print $1}'"


static int __get_link_path(const char* link, char *path, unsigned int len) {
    int ret;

    ret = readlink(link, path, len - 1);
    if (ret < 0 || ret >= (len - 1)) {
        fprintf(stderr, "get glibc readlink fail.\n");
        return -1;
    }

    return 0;
}

static int __do_get_glibc_path_host(char *path, unsigned int len) {
    int ret;
    FILE *f;
    char line[LEN_BUF];

    path[0] = 0;
    line[0] = 0;

    f = popen(COMMAND_GLIBC_PATH, "r");
    if (f == NULL) {
        return -1;
    }

    if (NULL == fgets(line, LEN_BUF, f)) {
        (void)pclose(f);
        return -1;
    }

    ret = __get_link_path((const char *)line, path, len);
    if (ret < 0) {
        (void)pclose(f);
        return -1;
    }

    (void)pclose(f);
    return 0;
}

static int __do_get_glibc_path_container(const char *container_id, char *path, unsigned int len) {
    int ret;
    char container_abs_path[PATH_LEN];
    char glibc_path[PATH_LEN];
    char glibc_abs_path[PATH_LEN];

    container_abs_path[0] = 0;
    glibc_path[0] = 0;
    glibc_abs_path[0] = 0;

    ret = get_container_merged_path(container_id, container_abs_path, PATH_LEN);
    if (ret < 0) {
        return ret;
    }

    ret = exec_container_command(container_id, COMMAND_GLIBC_PATH, glibc_path, PATH_LEN);
    if (ret < 0) {
        return ret;
    }

    (void)snprintf(glibc_abs_path, PATH_LEN, "%s/%s", container_abs_path, glibc_path);
    ret = __get_link_path((const char *)glibc_abs_path, path, len);
    if (ret < 0) {
        return -1;
    }

    return 0;
}

int get_glibc_path(const char *container_id, char *path, unsigned int len) {
    if (container_id == NULL || container_id[0] == 0) {
        return __do_get_glibc_path_host(path, len);
    }

    return __do_get_glibc_path_container(container_id, path, len);
}


