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
 * Author: Mr.lu
 * Create: 2022-5-30
 * Description: 
 ******************************************************************************/
#ifndef __GOPHER_HASH_H__
#define __GOPHER_HASH_H__

#include <uthash.h>


#define H_HANDLE   UT_hash_handle hh

#define H_FIND(head_ptr, k_ptr, k_len, result_ptr)   HASH_FIND(hh, head_ptr, k_ptr, k_len, result_ptr)
#define H_DEL(head_ptr, del_ptr)   HASH_DELETE(hh, head_ptr, del_ptr)
#define H_COUNT(head_ptr)   HASH_CNT(hh, head_ptr)
#define H_ADD(head_ptr, k_field_name, k_len, item_ptr)   HASH_ADD(hh, head_ptr, k_field_name, k_len, item_ptr)
#define H_ADD_KEYPTR(head_ptr, k_ptr, k_len, item_ptr)   HASH_ADD_KEYPTR(hh, head_ptr, k_ptr, k_len, item_ptr)

#define H_ITER(head_ptr, item_ptr, tmp_item_ptr) HASH_ITER(hh, head_ptr, item_ptr, tmp_item_ptr)

#endif
