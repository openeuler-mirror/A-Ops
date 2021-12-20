#include <stdio.h>
#include <string.h>

/*
eg:
[root@k8s-node2 net]# /usr/bin/df -i | awk 'NR>1 {print $2":"$3":"$4":"$5}'
Inodes:IUsed:IFree:IUse
65536:413:65123:1%
*/

#define METRICS_NAME "system_inode"
#define METRICS "/usr/bin/df -i | awk 'NR>1 {print $2\":\"$3\":\"$4\":\"$5}'"
#define LEN_BUF	256

#define METRICS_INODES 			0
#define METRICS_IUSED 			1
#define METRICS_IFREE 			2
#define METRICS_IUSE_PER 		3
#define METRICS_MAX				4


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
			(void)pclose(f);
			return -1;
		}
		p = strtok(line, ":");
		while (p != NULL && index < METRICS_MAX) {
			pp[index++] = p;
			p = strtok(NULL, ":");
		}
		fprintf(stdout, "|%s|%s|%s|%s|%s|\n",
			METRICS_NAME,
			pp[METRICS_IUSED], 
			pp[METRICS_IUSED], 
			pp[METRICS_IFREE], 
			pp[METRICS_IUSE_PER]);
	}

    (void)pclose(f);

    return 0;
}
