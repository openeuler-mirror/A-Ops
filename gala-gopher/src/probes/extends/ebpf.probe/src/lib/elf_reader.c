/******************************************************************************
 * Copyright (c) Huawei Technologies Co., Ltd. 2021. All rights reserved.
 * gala-gopher licensed under the Mulan PSL v2.
 * You can use this software according to the terms and conditions of the Mulan PSL v2.
 * You may obtain a copy of Mulan PSL v2 at:
 *     http://license.coscl.org.cn/MulanPSL2
 * THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
 * PURPOSE.
 * See the Mulan PSL v2 for more details.
 * Author: dowzyx
 * Create: 2021-12-08
 * Description: elf parse
 ******************************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdbool.h>
#include <gelf.h>
#include <sys/stat.h>
#include <errno.h>

#include "bpf.h"
#include "elf_reader.h"
#include "container.h"

#define SYSTEM_PATH_LEN 1024
#define DEFAULT_PATH_LIST   "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin"

#define COMMAND_REAL_PATH "/usr/bin/realpath %s"

#define COMMAND_GLIBC_PATH \
    "/usr/bin/ldd /bin/ls | grep \"libc.so\" | awk -F '=>' '{print $2}' | awk '{print $1}'"
#define COMMAND_ENV_PATH    "/usr/bin/env | grep PATH | awk -F '=' '{print $2}'"

#if BPF_ELF_DESC("get glibc path")
static int __get_link_path(const char* link, char *path, unsigned int len)
{
    char command[COMMAND_LEN];

    command[0] = 0;
    (void)snprintf(command, COMMAND_LEN, COMMAND_REAL_PATH, link);
    return exec_cmd(command, path, len);
}

static int __do_get_glibc_path_host(char *path, unsigned int len)
{
    int ret;
    FILE *f = NULL;
    char line[LINE_BUF_LEN];

    path[0] = 0;
    line[0] = 0;

    f = popen(COMMAND_GLIBC_PATH, "r");
    if (f == NULL)
        return -1;

    if (fgets(line, LINE_BUF_LEN, f) == NULL) {
        (void)pclose(f);
        return -1;
    }

    split_newline_symbol(line);
    ret = __get_link_path((const char *)line, path, len);
    if (ret < 0) {
        (void)pclose(f);
        return -1;
    }

    (void)pclose(f);
    return 0;
}

static int __do_get_glibc_path_container(const char *container_id, char *path, unsigned int len)
{
    int ret;
    char container_abs_path[PATH_LEN];
    char glibc_path[PATH_LEN];
    char glibc_abs_path[PATH_LEN];

    container_abs_path[0] = 0;
    glibc_path[0] = 0;
    glibc_abs_path[0] = 0;

    ret = get_container_merged_path(container_id, container_abs_path, PATH_LEN);
    if (ret < 0)
        return ret;

    ret = exec_container_command(container_id, COMMAND_GLIBC_PATH, glibc_path, PATH_LEN);
    if (ret < 0)
        return ret;

    (void)snprintf(glibc_abs_path, PATH_LEN, "%s/%s", container_abs_path, glibc_path);

    split_newline_symbol(glibc_abs_path);
    ret = __get_link_path((const char *)glibc_abs_path, path, len);
    if (ret < 0)
        return -1;

    return 0;
}

int get_glibc_path(const char *container_id, char *path, unsigned int len)
{
    if (container_id == NULL || container_id[0] == 0)
        return __do_get_glibc_path_host(path, len);

    return __do_get_glibc_path_container(container_id, path, len);
}
#endif

#if BPF_ELF_DESC("get exec path")
static bool __is_exec_file(const char *abs_path)
{
    struct stat st;

    if (stat(abs_path, &st) < 0)
        return false;

    if (st.st_mode & S_IEXEC)
        return true;

    return false;
}

static int __do_get_path_from_host(const char *binary_file, char **res_buf, int res_len)
{
    int r_len = 0;
    char *p = NULL;
    char *syspath_ptr = getenv("PATH");
    char syspath[PATH_LEN];

    if (syspath_ptr == NULL) {
        (void)snprintf((void *)syspath, PATH_LEN, "%s", DEFAULT_PATH_LIST);
        syspath_ptr = syspath;
    }

    p = strtok(syspath_ptr, ":");
    while (p != NULL) {
        char abs_path[PATH_LEN] = {0};
        (void)snprintf((char *)abs_path, PATH_LEN, "%s/%s", p, binary_file);
        if (__is_exec_file(abs_path)) {
            if (r_len >= res_len) {
                printf("host abs_path's num[%d] beyond res_buf's size[%d].\n", r_len, res_len);
                break;
            }
            res_buf[r_len] = (char *)malloc(PATH_LEN * sizeof(char));
            (void)snprintf(res_buf[r_len], PATH_LEN, "%s", abs_path);
            r_len++;
        }
        p = strtok(NULL, ":");
    }

    return r_len;
}

static int __do_get_path_from_container(const char *binary_file, const char *container_id, char **res_buf, int res_len)
{
    int ret = -1;
    int r_len = 0;
    char *p = NULL;
    char syspath[PATH_LEN] = {0};
    char container_abs_path[PATH_LEN] = {0};

    ret = get_container_merged_path(container_id, container_abs_path, PATH_LEN);
    if (ret < 0) {
        printf("get container merged_path fail.\n");
        return ret;
    }

    ret = exec_container_command(container_id, COMMAND_ENV_PATH, syspath, PATH_LEN);
    if (ret < 0) {
        printf("get container's env PATH fail.\n");
        return ret;
    }

    if (syspath[0] == 0)
        (void)snprintf((void *)syspath, PATH_LEN, "%s", DEFAULT_PATH_LIST);

    p = strtok((void *)syspath, ":");
    while (p != NULL) {
        char abs_path[PATH_LEN] = {0};
        (void)snprintf((char *)abs_path, PATH_LEN, "%s%s/%s", container_abs_path, p, binary_file);
        if (__is_exec_file(abs_path)) {
            if (r_len >= res_len) {
                printf("container abs_path's num[%d] beyond res_buf's size[%d].\n", r_len, res_len);
                break;
            }
            res_buf[r_len] = (char *)malloc(PATH_LEN * sizeof(char));
            (void)snprintf(res_buf[r_len], PATH_LEN, "%s", abs_path);
            r_len++;
        }
        p = strtok(NULL, ":");
    }

    return r_len;
}

int get_exec_file_path(const char *binary_file, const char *specified_path, const char *container_id,
                        char **res_buf, int res_len)
{
    int ret_path_num = -1;

    if (binary_file == NULL || !strcmp(binary_file, "NULL")) {
        printf("please input binary_file name.\n");
        return -1;
    }
    /* specified file path */
    if (specified_path != NULL && strlen(specified_path)) {
        if (!__is_exec_file(specified_path)) {
            printf("specified path check error[%d].\n", errno);
            return -1;
        }
        res_buf[0] = (char *)malloc(PATH_LEN * sizeof(char));
        (void)snprintf(res_buf[0], PATH_LEN, "%s", specified_path);
        return 1;
    }

    if (container_id == NULL || !strcmp(container_id, "NULL")) {
        /* exec file in host */
        ret_path_num = __do_get_path_from_host(binary_file, res_buf, res_len);
    } else {
        /* exec file in container */
        ret_path_num = __do_get_path_from_container(binary_file, container_id, res_buf, res_len);
    }

    if (ret_path_num == 0) {
        printf("no executable in system default path, please specify abs_path.\n");
        return -1;
    }
    return ret_path_num;
}

void free_exec_path_buf(char **ptr, int len)
{
    for (int i = 0; i < len; i++) {
        if (ptr[i] != NULL) {
            free(ptr[i]);
            ptr[i] = NULL;
        }
    }
}
#endif

#if BPF_ELF_DESC("get sym's offset from elf file")
static int _find_sym(const char *sym_name, uint64_t addr, uint64_t len, void *payload)
{
    struct symbol_info *sym = (struct symbol_info *)payload;
    if (!strcmp(sym->name, sym_name)) {
        sym->offset = addr;
        return -1;
    }
    return 0;
}

static int openelf(const char *path, Elf **elf_out, int *fd_out)
{
    *fd_out = open(path, O_RDONLY);
    if (*fd_out < 0)
        return -1;

    if (elf_version(EV_CURRENT) == EV_NONE) {
        close(*fd_out);
        return -1;
    }

    *elf_out = elf_begin(*fd_out, ELF_C_READ, 0);
    if (*elf_out == NULL) {
        close(*fd_out);
        return -1;
    }

    return 0;
}

static int __elf_get_type(const char *path)
{
    Elf *e = NULL;
    GElf_Ehdr hdr;
    int fd = -1;
    void* res = NULL;

    if (openelf(path, &e, &fd) < 0)
        return -1;

    res = (void*)gelf_getehdr(e, &hdr);
    elf_end(e);
    close(fd);

    if (res == NULL)
        return -1;

    return hdr.e_type;
}

static int __elf_foreach_load_section(const char *path, void *payload)
{
    Elf *e = NULL;
    int fd = -1;
    int err = -1;
    size_t nhdrs = 0;
    struct load_info *load = (struct load_info *)payload;

    if (openelf(path, &e, &fd) < 0)
        goto exit;

    if (elf_getphdrnum(e, &nhdrs) != 0)
        goto exit;

    GElf_Phdr header;
    for (int i = 0; i < nhdrs; i++) {
        if (!gelf_getphdr(e, i, &header))
            continue;

        if (header.p_type != PT_LOAD || !(header.p_flags & PF_X))
            continue;

        load->binary_vaddr  = header.p_vaddr;
        load->binary_offset = header.p_offset;
        load->binary_memsz  = header.p_memsz;
        break;
    }
    err = 0;

exit:
    if (e != NULL)
        elf_end(e);

    if (fd >= 0)
        close(fd);

    return err;
}

static int __list_in_scn(Elf *e, Elf_Scn *section, size_t stridx, size_t symsize, struct symbol_info_option *option,
                        elf_symcb callback, elf_symcb_lazy callback_lazy, void *payload, bool debugfile)
{
    Elf_Data *data = NULL;

    if (symsize == 0)
        return -1;

    while ((data = elf_getdata(section, data)) != 0) {
        size_t symcount = data->d_size / symsize;

        if (data->d_size % symsize)
            return -1;

        for (int i = 0; i < symcount; ++i) {
            GElf_Sym sym;
            const char *name = NULL;
            size_t name_len = 0;

            if (!gelf_getsym(data, (int)i, &sym))
                continue;

            name = elf_strptr(e, stridx, sym.st_name);
            if (name == NULL || name[0] == 0)
                continue;

            name_len = strlen(name);
            if (sym.st_value == 0)
                continue;

            uint32_t st_type = ELF_ST_TYPE(sym.st_info);
            if (!(option->use_symbol_type & (1 << st_type)))
                continue;

            int ret = -1;
            if (option->lazy_symbolize) {
                ret = callback_lazy(stridx, sym.st_name, name_len, sym.st_value,
                                    sym.st_size, debugfile, payload);
            } else {
                ret = callback(name, sym.st_value, sym.st_size, payload);
            }
            if (ret < 0)
                return 1;      // signal termination to caller
        }
    }
    return 0;
}

static int __listsymbols(Elf *e, elf_symcb callback, elf_symcb_lazy callback_lazy,
                        void *payload, struct symbol_info_option *option, bool debugfile)
{
    Elf_Scn *section = NULL;

    while ((section = elf_nextscn(e, section)) != 0) {
        GElf_Shdr header;
        if (!gelf_getshdr(section, &header))
            continue;
        /* SHT_SYMTAB -  2 - [Symbol table] */
        /* SHT_DYNSYM - 11 - [Dynamic linker symbol table] */
        if (header.sh_type != SHT_SYMTAB && header.sh_type != SHT_DYNSYM)
            continue;

        int rc = __list_in_scn(e, section, header.sh_link, header.sh_entsize,
                                option, callback, callback_lazy, payload, debugfile);
        if (rc == 1)
            break;      // callback signaled termination

        if (rc < 0)
            return rc;
    }

    return 0;
}

static int __foreach_sym_core(const char *path, elf_symcb callback, elf_symcb_lazy callback_lazy,
                            struct symbol_info_option *option, void *payload, int debugfile)
{
    Elf *e = NULL;
    int fd = -1;
    int res = -1;

    res = openelf(path, &e, &fd);
    if (option == NULL || res < 0)
        return -1;

    if (option->use_debug_file && debugfile == NOT_DEBUG_FILE) {
        if (path != NULL)
            __foreach_sym_core(path, callback, callback_lazy, option, payload, IS_DEBUG_FILE);
    }

    res = __listsymbols(e, callback, callback_lazy, payload, option, debugfile);
    elf_end(e);
    close(fd);
    return 0;
}

static int elf_reader_foreach_sym(const char *path, elf_symcb callback, void *option, void *payload)
{
    struct symbol_info_option *o = option;
    o->lazy_symbolize = 0;
    return __foreach_sym_core(path, callback, NULL, o, payload, IS_DEBUG_FILE);
}

#if 0
static int elf_reader_foreach_sym_lazy(const char *path, elf_symcb_lazy callback, void *option, void *payload)
{
    struct symbol_info_option *o = option;
    o->lazy_symbolize = 1;
    return __foreach_sym_core(path, NULL, callback, o, payload, IS_DEBUG_FILE);
}
#endif

int resolve_symbol_infos(const char *bin_path, const char *sym_name,
                         struct symbol_info_option *option, uint64_t *sym_offset)
{
    int err = -1;
    int module_type = 0;
    struct symbol_info sym = {0};
    struct load_info load = {0};
    static struct symbol_info_option default_option = {
        .use_debug_file = 1,
        .check_debug_file_crc = 1,
        .lazy_symbolize = 1,
        .use_symbol_type = BCC_SYM_ALL_TYPES,
    };

    if (bin_path == NULL || sym_name == NULL) {
        printf(" resolve_symbol_infos para bin_path or sym_name is NULL.\n");
        return -1;
    }

    if (option == NULL)
        option = &default_option;
    /* 1. sym_name's infos from section symtab or dynsym */
    sym.module = strdup(bin_path);
    sym.name = strdup(sym_name);
    sym.offset = 0x0;
    if (sym.name) {
        if (elf_reader_foreach_sym((const char *)sym.module, _find_sym, option, &sym) < 0) {
            printf(" foreach_sym module[%s] sym[%s] fail.\n", sym.module, sym.name);
            goto invalid_module;
        }
    }
    if (sym.offset == 0) {
        printf(" foreach_sym sym's offset is 0.\n");
        goto invalid_module;
    }

    /* 2. translate the virtual address to physical address in the binary file. */
    module_type = __elf_get_type((const char *)sym.module);
    if (module_type == ET_EXEC || module_type == ET_DYN) {
        if (__elf_foreach_load_section((const char *)sym.module, &load) < 0) {
            printf(" resolve_symbol_infos foreach_load_section fail.\n");
            goto invalid_module;
        }
    }

    /* 3. calculate symbol offset : sym.offset - load.binary_vaddr */
    if (sym.offset >= load.binary_vaddr && sym.offset < (load.binary_vaddr + load.binary_memsz)) {
        *sym_offset = sym.offset - load.binary_vaddr + load.binary_offset;
        err = 0;
    } else {
        printf(" resolve_symbol_infos err, sym_off(%lu) beyond (%lu ~ %lu).\n",
                            sym.offset, load.binary_vaddr, load.binary_vaddr + load.binary_memsz);
        goto invalid_module;
    }

invalid_module:
    if (sym.module != NULL) {
        free(sym.module);
        sym.module = NULL;
    }
    if (sym.name != NULL) {
        free(sym.name);
        sym.name = NULL;
    }

    return err;
}
#endif
