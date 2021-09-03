#######################################################################################
#
# Copyright (c) Huawei Technologies Co., Ltd. 2019. All rights reserved.
# security-tool licensed under the Mulan PSL v1.
# You can use this software according to the terms and conditions of the Mulan PSL v1.
# You may obtain a copy of Mulan PSL v1 at:
#     http://license.coscl.org.cn/MulanPSL
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v1 for more details.
# Description: Append the history list to the history file.
#
#######################################################################################

set LastComandNum_for_history
alias precmd 'source /etc/csh.precmd'

umask 0077
