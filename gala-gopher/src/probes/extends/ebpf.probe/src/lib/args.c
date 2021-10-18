#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <getopt.h>

#include "args.h"

#define OUT_PUT_PERIOD_MAX     (120)	// 2mim
#define OUT_PUT_PERIOD_MIN     (1)		// 1s

// gala-gopher.conf only support one arg, used set out put period
int __period_arg_parse(char opt, char *arg, int idx, unsigned int *val)
{
    if (opt != 't' || !arg) {
        return -1;
    }

    unsigned int interval = (unsigned int)atoi(arg);
    if (interval < OUT_PUT_PERIOD_MIN || interval > OUT_PUT_PERIOD_MAX) {
        return -1;
    }
    val = interval;
    return 0;
}


int __args_parse(int argc, char **argv, char *opt_str, struct probe_params* params) {
    int ch;
	unsigned int val;
	
    if (!opt_str) {
        return -1;
    }
    while ((ch = getopt(argc, argv, opt_str)) != -1) {
        if (!optarg) {
            return -1;
        }
        if (__period_arg_parse(ch, optarg, optind, &val) == 0) {
			params->period = val;
        }
    }
    return 0;
}

int args_parse(int argc, char **argv, char *opt_str, struct probe_params* params) {
	return __args_parse(argc, argv, opt_str, params);
}

