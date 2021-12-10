#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdbool.h>
#include <gelf.h>
#include "elf_reader.h"
#include "container.h"

#define LEN_BUF 256
#define COMMAND_LEN 512
#define PATH_LEN 512

#define COMMAND_GLIBC_PATH \
    "/usr/bin/ldd /bin/ls | grep \"libc.so\" | awk -F '=>' '{print $2}' | awk '{print $1}'"


static int __get_link_path(const char* link, char *path, unsigned int len) {
    int ret;

    ret = readlink(link, path, len - 1);
    if (ret < 0 || ret >= (len - 1)) {
        fprintf(stderr, "get glibc readlink fail.\n");
        return -1;
    }

    return 0;
}

static int __do_get_glibc_path_host(char *path, unsigned int len) {
    int ret;
    FILE *f;
    char line[LEN_BUF];

    path[0] = 0;
    line[0] = 0;

    f = popen(COMMAND_GLIBC_PATH, "r");
    if (f == NULL) {
        return -1;
    }

    if (NULL == fgets(line, LEN_BUF, f)) {
        (void)pclose(f);
        return -1;
    }

    ret = __get_link_path((const char *)line, path, len);
    if (ret < 0) {
        (void)pclose(f);
        return -1;
    }

    (void)pclose(f);
    return 0;
}

static int __do_get_glibc_path_container(const char *container_id, char *path, unsigned int len) {
    int ret;
    char container_abs_path[PATH_LEN];
    char glibc_path[PATH_LEN];
    char glibc_abs_path[PATH_LEN];

    container_abs_path[0] = 0;
    glibc_path[0] = 0;
    glibc_abs_path[0] = 0;

    ret = get_container_merged_path(container_id, container_abs_path, PATH_LEN);
    if (ret < 0) {
        return ret;
    }

    ret = exec_container_command(container_id, COMMAND_GLIBC_PATH, glibc_path, PATH_LEN);
    if (ret < 0) {
        return ret;
    }

    (void)snprintf(glibc_abs_path, PATH_LEN, "%s/%s", container_abs_path, glibc_path);
    ret = __get_link_path((const char *)glibc_abs_path, path, len);
    if (ret < 0) {
        return -1;
    }

    return 0;
}

int get_glibc_path(const char *container_id, char *path, unsigned int len) {
    if (container_id == NULL || container_id[0] == 0) {
        return __do_get_glibc_path_host(path, len);
    }

    return __do_get_glibc_path_container(container_id, path, len);
}

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
    if (*fd_out < 0) {
        return -1;
    }
    
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

    if (openelf(path, &e, &fd) < 0) {
        return -1;
    }

    res = (void*)gelf_getehdr(e, &hdr);
    elf_end(e);
    close(fd);

    if (!res) {
        return -1;
    }
    return hdr.e_type;
}

static int __elf_foreach_load_section(const char *path, void *payload)
{
    Elf *e = NULL;
    int fd = -1;
    int err = -1;
    size_t nhdrs = 0;
    struct load_info *load = (struct load_info *)payload;

    if (openelf(path, &e, &fd) < 0) {
        goto exit;
    }

    if (elf_getphdrnum(e, &nhdrs) != 0) {
        goto exit;
    }

    GElf_Phdr header;
    for (int i = 0; i < nhdrs; i++) {
        if (!gelf_getphdr(e, i, &header)) {
            continue;
        }
        if (header.p_type != PT_LOAD || !(header.p_flags & PF_X)) {
            continue;
        }
        load->binary_vaddr  = header.p_vaddr;
        load->binary_offset = header.p_offset;
        load->binary_memsz  = header.p_memsz;
        break;
    }
    err = 0;

exit:
    if (e) {
        elf_end(e);
    }
    if (fd >= 0) {
        close(fd);
    }
    return err;
}

static int __list_in_scn(Elf *e, Elf_Scn *section, size_t stridx, size_t symsize, struct symbol_info_option *option,
                        elf_symcb callback, elf_symcb_lazy callback_lazy, void *payload, bool debugfile)
{
    Elf_Data *data = NULL;

    while ((data = elf_getdata(section, data)) != 0) {
        size_t symcount = data->d_size / symsize;

        if (data->d_size % symsize) {
            return -1;
        }

        for (int i = 0; i < symcount; ++i) {
            GElf_Sym sym;
            const char *name = NULL;
            size_t name_len = 0;

            if (!gelf_getsym(data, (int)i, &sym)) {
                continue;
            }

            name = elf_strptr(e, stridx, sym.st_name);
            if (name == NULL || name[0] == 0) {
                continue;
            }

            name_len = strlen(name);
            if (sym.st_value == 0) {
                continue;
            }

            uint32_t st_type = ELF_ST_TYPE(sym.st_info);
            if (!(option->use_symbol_type & (1 << st_type))) {
                continue;
            }

            int ret = -1;
            if (option->lazy_symbolize) {
                ret = callback_lazy(stridx, sym.st_name, name_len, sym.st_value,
                                    sym.st_size, debugfile, payload);
            } else {
                ret = callback(name, sym.st_value, sym.st_size, payload);
            }
            if (ret < 0) {
                return 1;      // signal termination to caller
            }
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
        if (!gelf_getshdr(section, &header)) {
            continue;
        }
        /* SHT_SYMTAB -  2 - [Symbol table] */
        /* SHT_DYNSYM - 11 - [Dynamic linker symbol table] */
        if (header.sh_type != SHT_SYMTAB && header.sh_type != SHT_DYNSYM) {
            continue;
        }

        int rc = __list_in_scn(e, section, header.sh_link, header.sh_entsize,
                                option, callback, callback_lazy, payload, debugfile);
        if (rc == 1) {
            break;      // callback signaled termination
        }
        if (rc < 0) {
            return rc;
        }
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
    if (!option || res < 0) {
        return -1;
    }

    if (option->use_debug_file && debugfile == NOT_DEBUG_FILE) {
        if (path) {
            __foreach_sym_core(path, callback, callback_lazy, option, payload, IS_DEBUG_FILE);
        }
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

static int elf_reader_foreach_sym_lazy(const char *path, elf_symcb_lazy callback, void *option, void *payload) 
{
    struct symbol_info_option *o = option;
    o->lazy_symbolize = 1;
    return __foreach_sym_core(path, NULL, callback, o, payload, IS_DEBUG_FILE);
}

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

    if (option == NULL) {
        option = &default_option;
    }
    /* 1. sym_name's infos from section symtab or dynsym */
    sym.module = strdup(bin_path);
    sym.name = strdup(sym_name);
    sym.offset = 0x0;
    if (sym.name) {
        if (elf_reader_foreach_sym(sym.module, _find_sym, option, &sym) < 0) {
            printf(" resolve_symbol_infos foreach_sym fail.\n");
            goto invalid_module;
        }
    }
    if (sym.offset == 0) {
        printf(" resolve_symbol_infos foreach sym's offset is 0.\n");
        goto invalid_module;
    }

    /* 2. translate the virtual address to physical address in the binary file. */
    module_type = __elf_get_type(sym.module);
    if (module_type == ET_EXEC || module_type == ET_DYN) {
        if (__elf_foreach_load_section(sym.module, &load) < 0) {
            printf(" resolve_symbol_infos foreach_load_section fail.\n");
            goto invalid_module;
        }
    }

    /* 3. calculate symbol offset : sym.offset - load.binary_vaddr */
    if (sym.offset >= load.binary_vaddr && sym.offset < (load.binary_vaddr + load.binary_memsz)) {
        *sym_offset = sym.offset - load.binary_vaddr + load.binary_offset;
        err = 0;
    } else {
        printf(" resolve_symbol_infos err, sym_off(%lld) beyond (%lld ~ %lld).\n", 
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

