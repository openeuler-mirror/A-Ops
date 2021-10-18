#ifndef __GOPHER_ARGS_H__
#define __GOPHER_ARGS_H__


struct probe_params {
	unsigned int period;
};
int args_parse(int argc, char **argv, char *opt_str, struct probe_params* params);

#endif
