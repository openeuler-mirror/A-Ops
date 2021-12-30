#ifndef __GOPHER_ARGS_H__
#define __GOPHER_ARGS_H__

#define MAX_PATH_LEN	512
struct probe_params {
    unsigned int period;
    char elf_path[MAX_PATH_LEN];
};
int args_parse(int argc, char **argv, char *opt_str, struct probe_params* params);

#endif
