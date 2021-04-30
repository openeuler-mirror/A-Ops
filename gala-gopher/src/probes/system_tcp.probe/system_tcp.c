#include <stdio.h>
#include <string.h>

/*
eg:
[root@k8s-node2 net]# /usr/bin/cat /proc/net/tcp | awk 'NR>1 {print $2":"$3":"$4":"$7}'
local_address:local_port:rem_address:rem_port:st:retrnsmt
00000000:0016:00000000:0000:0A:00000000
*/

#define METRICS_NAME "system_tcp"
#define METRICS "/usr/bin/cat /proc/net/tcp | awk 'NR>1 {print $2\":\"$3\":\"$4\":\"$7}'"
#define LEN_BUF	256

#define METRICS_LOCAL_ADDRESS 	0
#define METRICS_LOCAL_PORT 		1
#define METRICS_REM_ADDRESS 	2
#define METRICS_REM_PORT 		3
#define METRICS_ST 				4
#define METRICS_RETRNSMT 		5
#define METRICS_MAX				6


int main()
{
	char line[LEN_BUF];
    FILE *f = NULL;
	int index;
	char *p;
	char *pp[METRICS_MAX];

	f = popen(METRICS, "r");
	if (f == NULL) {
		return -1;
	}

	while (!feof(f)) {
		(void)memset(line, 0, LEN_BUF);
		index = 0;
		if (NULL == fgets(line, LEN_BUF, f)) {
			(void)fclose(f);
			return -1;
		}
		p = strtok(line, ":");
		while (p != NULL && index < METRICS_MAX) {
			pp[index++] = p;
			p = strtok(NULL, ":");
		}
		fprintf(stdout, "|%s|%s|%s|%s|%s|%s|%s|\n",
			METRICS_NAME,
			pp[METRICS_LOCAL_ADDRESS], 
			pp[METRICS_LOCAL_PORT], 
			pp[METRICS_REM_ADDRESS], 
			pp[METRICS_REM_PORT], 
			pp[METRICS_ST], 
			pp[METRICS_RETRNSMT]);
	}

    (void)fclose(f);

    return 0;
}
