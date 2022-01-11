/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
 */
#ifndef __ELF_READER_H__
#define __ELF_READER_H__

#define BPF_ELF_DESC(desc) 1

#define IS_DEBUG_FILE   1
#define NOT_DEBUG_FILE  0
#define ELF_ST_TYPE(x)  (((uint32_t) (x)) & 0xf)
#define BCC_SYM_ALL_TYPES   65535

struct symbol_info {
    const char *name;
    const char *demangle_name;
    const char *module;
    uint64_t offset;
};

struct load_info {
    uint64_t binary_vaddr;
    uint64_t binary_memsz;
    uint64_t binary_offset;
};

struct symbol_info_option {
    int use_debug_file;
    int check_debug_file_crc;
    // Symbolize on-demand or symbolize everything ahead of time
    int lazy_symbolize;
    // Bitmask flags indicating what types of ELF symbols to use
    uint32_t use_symbol_type;
};

// Symbol name, start address, length, payload
// Callback returning a negative value indicates to stop the iteration
typedef int (*elf_symcb)(const char *, uint64_t, uint64_t, void *);
// Section idx, str table idx, str length, start address, length, payload
typedef int (*elf_symcb_lazy)(size_t, size_t, size_t, uint64_t, uint64_t, int, void *);

// Return 0 on success and -1 on failure. Output will be write to sym.
int resolve_symbol_infos(const char *bin_path, const char *sym_name,
                         struct symbol_info_option *option, uint64_t *sym_offset);

int get_glibc_path(const char *container_id, char *path, unsigned int len);

int get_exec_file_path(const char *binary_file, const char *specified_path, const char *container_id,
                        char **res_buf, int res_len);

void free_exec_path_buf(char **ptr, int len);

#endif
