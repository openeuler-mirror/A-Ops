#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "event.h"

#define LOG_MESSAGES "/var/log/messages"
#define CMD_FILE_LINE_NUM "/usr/bin/wc -l %s | awk '{print $1}'"
#define CMD_EVENT_CODE_ABNORMAL "/usr/bin/sed -n '%u,%up' %s |grep 'code=\\[[1-9][0-9]*\\]'"

#define LEN_BUF	  64
#define LEN_CMD	  128
#define LEN_LINE  1024

static int g_lastLogLineNum = 0;

void print_event_output(struct event_data *event){
    char timestamp[LEN_BUF] = {0};
    sprintf(timestamp, "%llu", event->timestamp);  

    fprintf(stdout, "|%s|%s|%s|%s|\n",
        "event",
        timestamp,
        event->level, 
        event->body
    );
    // fflush(stdout);
}

static int get_file_line_num(const char * filename)
{
   int ret = 0; 
   FILE *f = NULL;
   char count[LEN_BUF];
   char cmd[LEN_CMD] = {0};

   sprintf(cmd, CMD_FILE_LINE_NUM, LOG_MESSAGES);

   f = popen(cmd, "r");
   if (f == NULL) {
       return -1;
   }

   if (!feof(f)) {
       fgets(count, LEN_BUF, f);
   }

   ret = atoi(count);

   (void)pclose(f);

   return ret;
}

static void make_event(char * log){
    struct event_data event = {0};
    
    time_t now;
    time(&now);
    event.timestamp = now*1000*1000*1000;

    strcpy(event.body, log);
    strcpy(event.level, EVENT_LEVEL_ERROR);
    print_event_output(&event);
}

static int filter_log_event()
{
    FILE *f = NULL;
    char line[LEN_LINE];
    char cmd[LEN_CMD] = {0};
    
    int lineNum = get_file_line_num(LOG_MESSAGES);
    if (lineNum < 1) {
       return -1;
    }
    
    // init g_lastLogLineNum, from current file bottom line
    if (g_lastLogLineNum == 0){
        g_lastLogLineNum = lineNum;
    }
    if (g_lastLogLineNum - lineNum == 1) {    // file line readed
        return 0;
    }else if(g_lastLogLineNum - lineNum > 1){ // log file rewrite from beginning
        g_lastLogLineNum = 1;
    }

    sprintf(cmd, CMD_EVENT_CODE_ABNORMAL, g_lastLogLineNum, lineNum, LOG_MESSAGES);
    // printf("EVENT.PROBE: event code abnormal is : %s\n", cmd); 

    f = popen(cmd, "r");
    if (f == NULL) {
        return -1; 
    }

    while (!feof(f)) {
        fgets(line, LEN_LINE, f);
        if (strlen(line) > 0) {
            if (line[strlen(line)-1] == '\n'){
                line[strlen(line)-1] = '\0'; 
            }
            make_event(line);
            sprintf(line, ""); 
        }
    }

    g_lastLogLineNum = lineNum + 1;

    (void)pclose(f); 

    return 0;
}

int main(int argc, char **argv)
{
    int ret = filter_log_event();
    if (ret != 0) {
        return -1;
    }

    return 0;
}
