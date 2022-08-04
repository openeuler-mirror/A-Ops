#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
from aops_check.core.experiment.algorithm.base_algo import BaseMultiItemAlgorithmTwo


class StatisticalCheck(BaseMultiItemAlgorithmTwo):

    def __init__(self, percent: float = 0.5):
        self._percent = percent

    def calculate(self, data: dict) -> bool:
        """
        overload calculate function
        Args:
            data: result of single item check, like {"cpu_load15": True, "rx_error": False}

        Returns:
            bool
        """
        abnormal_num = 0
        for value in data.values():
            if value:
                abnormal_num += 1

        if abnormal_num / len(data) > self._percent:
            return True
        return False
