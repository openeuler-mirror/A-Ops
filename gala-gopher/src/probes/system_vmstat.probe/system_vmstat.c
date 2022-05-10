 /*
  * Copyright (c) Huawei Technologies Co., Ltd. 2021-2022. All rights reserved.
  * iSulad licensed under the Mulan PSL v2.
  * You can use this software according to the terms and conditions of the Mulan PSL v2.
  * You may obtain a copy of Mulan PSL v2 at:
  *     http://license.coscl.org.cn/MulanPSL2
  * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
  * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
  * PURPOSE.
  * See the Mulan PSL v2 for more details.
  * Description: system vmstat probe
  */
#include <stdio.h>
#include <string.h>
#include "args.h"

#define SYSTEM_VMSTAT_FILE_PATH "/proc/vmstat"

#define SYSTEM_VMSTAT_MAX_LINE_LENGTH 2048
#define SYSTEM_VMSTAT_MAX_KEY_LENGTH  256
#define SYSTEM_VMSTAT_MAX_VAL_LENGTH  2048

struct system_vmstat_field {
    char *key;
    char val[SYSTEM_VMSTAT_MAX_VAL_LENGTH];
};

static struct system_vmstat_field g_system_vmstat_fields[] = {
    {"nr_free_pages",                       ""},
    {"nr_zone_inactive_anon",               ""},
    {"nr_zone_active_anon",                 ""},
    {"nr_zone_active_file",                 ""},
    {"nr_zone_unevictable",                 ""},
    {"nr_zone_write_pending",               ""},
    {"nr_mlock",                            ""},
    {"nr_page_table_pages",                 ""},
};

static int system_vmstat_parse_line(const char *line, char *key, char *value)
{
    char spliter = ' ';
    int line_length = strlen(line);
    int ret = 0;

    // get key
    int key_end = 0;
    for (key_end = 0; key_end < line_length; ++key_end) {
        if (line[key_end] == spliter) {
            break;
        }
    }
    if (key_end == line_length) {
        return -1;
    }
    memcpy(key, line, key_end);

    int val_start = 0;
    for (val_start = key_end + 1; val_start < line_length; ++val_start) {
        if (line[val_start] != ' ') {
            break;
        }
    }
    if (val_start == line_length) {
        return -1;
    }
    memcpy(value, line + val_start, line_length - val_start - 1);
    return 0;
}

static int system_vmstat_set_field(char *key, char *val)
{
    int field_num = sizeof(g_system_vmstat_fields) / sizeof(g_system_vmstat_fields[0]);
    for (int i = 0; i < field_num; ++i) {
        if (strcmp(g_system_vmstat_fields[i].key, key) == 0) {
            snprintf(g_system_vmstat_fields[i].val, SYSTEM_VMSTAT_MAX_VAL_LENGTH, "%s", val);
        }
    }
    return 0;
}

static int system_vmstat_print_records()
{
    fprintf(stdout, "|%s|%s|%s|%s|%s|%s|%s|%s|%s|\n",
        "system_vmstat",
        g_system_vmstat_fields[0].val,
        g_system_vmstat_fields[1].val,
        g_system_vmstat_fields[2].val,
        g_system_vmstat_fields[3].val,
        g_system_vmstat_fields[4].val,
        g_system_vmstat_fields[5].val,
        g_system_vmstat_fields[6].val,
        g_system_vmstat_fields[7].val
    );
    return 0;
}

int main(struct probe_params * params)
{
    int ret = 0;
    FILE *f = NULL;
    char buffer[SYSTEM_VMSTAT_MAX_LINE_LENGTH];
    char key[SYSTEM_VMSTAT_MAX_KEY_LENGTH];
    char val[SYSTEM_VMSTAT_MAX_VAL_LENGTH];

    f = fopen(SYSTEM_VMSTAT_FILE_PATH, "r");
    if (f == NULL) {
        return -1;
    }

    while (!feof(f)) {
        fgets(buffer, SYSTEM_VMSTAT_MAX_LINE_LENGTH, f);
        memset(key, 0, SYSTEM_VMSTAT_MAX_KEY_LENGTH);
        memset(val, 0, SYSTEM_VMSTAT_MAX_VAL_LENGTH);
        ret = system_vmstat_parse_line(buffer, key, val);
        if (ret != 0) {
            fclose(f);
            return -1;
        }
        system_vmstat_set_field(key, val);
    }
    fclose(f);

    system_vmstat_print_records();
    return 0;
}
