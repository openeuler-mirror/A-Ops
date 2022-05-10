#include <stdio.h>
#include <string.h>
#include "args.h"

void example_collect_data()
{
    fprintf(stdout, "|%s|%s|%s|%s|\n",
        "example",
        "10",
        "88",
        "15"
    );
}

int main(struct probe_params * params)
{
    example_collect_data();
    return 0;
}

