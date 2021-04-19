// sample code for TDengine subscribe/consume API
// to compile: gcc -o subscribe subscribe.c -ltaos

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <taos.h>  // include TDengine header file
#include <unistd.h>

#define TAOS_IP   "localhost"
#define TAOS_USER "root"
#define TAOS_PASS "taosdata"
#define TAOS_DB   "demo"
#define TAOS_PORT 0

#define TAOS_TOPIC "gala_gopher"
#define TAOS_SQL "select * from tt;"

void print_result(TAOS_RES* res, int blockFetch) {
    TAOS_ROW    row = NULL;
    int         num_fields = taos_num_fields(res);
    TAOS_FIELD* fields = taos_fetch_fields(res);
    int         nRows = 0;
    char        buf[4096];

    if (blockFetch) {
        nRows = taos_fetch_block(res, &row);
        //for (int i = 0; i < nRows; i++) {
        //  taos_print_row(buf, row + i, fields, num_fields);
        //  puts(buf);
        //}
    } else {
        while ((row = taos_fetch_row(res))) {
            taos_print_row(buf, row, fields, num_fields);
            puts(buf);
            nRows++;
        }
    }

    printf("%d rows consumed.\n", nRows);
}


int main() {
    int ret;
    TAOS *taos = taos_connect(TAOS_IP, TAOS_USER, TAOS_PASS, TAOS_DB, TAOS_PORT);
    if (taos == NULL) {

        printf("[EGRESS] failed to connect taosdb.\n");
        return 0;
    }

    TAOS_SUB *tSub = NULL;
    tSub = taos_subscribe(taos, 0, TAOS_TOPIC, TAOS_SQL, NULL, NULL, 0);
    for (;;) {
        TAOS_RES *res = taos_consume(tSub);
        if (res == NULL) {
            printf("failed to consume data.\n");
            break;
        } else {
            print_result(res, 0);
        }
        sleep(1);
    }
    
    return 0;
}

