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

function openEuler_history()
{
    local result=$?
    local result_str=""
    if [ ${result} -eq 0 ];then
        result_str="return code=[0], execute success"
    else
        result_str="return code=[${result}], execute failed"
    fi
    history -a
    local user=$(whoami)
    local user_id=$(id -ur $user)
    local login=$(who -m | awk '{print $2" "$NF}')
    local msg=$(history 1 | { read x y; echo "$y"; })
    local num=$(history 1 | { read x y; echo "$x"; })
    if [ "${num}" != "${LastComandNum_for_history}" ] && [ "${LastComandNum_for_history}" != "" -o "${num}" == "1" ];then
        logger -t "[${SHELL}]" "[${msg}]" "${result_str}" "by [${user}(uid=$user_id)] from [$login]"
    fi
    LastComandNum_for_history=${num}
}

function openEuler_variable_readonly()
{
    local var="$1"
    local val="$2"
    local ret=$(readonly -p | grep -w "${var}" | awk -F "${var}=" '{print $NF}')
    if [ "${ret}" = "\"${val}\"" ]
    then
        return
    else
        export "${var}"="${val}"
        readonly "${var}"
    fi
}

export HISTCONTROL=''
openEuler_variable_readonly HISTTIMEFORMAT ""
openEuler_variable_readonly PROMPT_COMMAND openEuler_history


umask 0077
