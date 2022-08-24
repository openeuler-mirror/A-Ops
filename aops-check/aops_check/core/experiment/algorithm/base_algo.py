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
from typing import Optional
from abc import ABCMeta, abstractmethod


class BaseSingleItemAlgorithm(metaclass=ABCMeta):
    """
    Base algorithm class. All algorithm should inherit this class
    """

    @abstractmethod
    def calculate(self, data: list, time_range: Optional[list] = None):
        """
        overload the calculate function
        Args:
            data: single item data with timestamp, like [[1658544527, '100'], [1658544527, '100']...]
            time_range: time range of checking. only error found in this range could be record

        Returns:
            list: abnormal data with timestamp, like [[1658544527, 100], [1658544527, 100]...]
        """
        pass

    def preprocess(self, data: list):
        """
        preprocess data
        """
        for single_data in data:
            single_data[1] = float(single_data[1])


class BaseMultiItemAlgorithmOne(metaclass=ABCMeta):
    """
    Base algorithm class. All multi item check algorithm which based on original data
    should inherit this class
    """

    @abstractmethod
    def calculate(self, data: dict, time_range: Optional[list] = None):
        """
        overload the calculate function
        Args:
            data: multi item data with timestamp, like
                {
                    "cpu_load15": [[1658544527, 100], [1658544527, 100]...],
                    "cpu_load1": [[1658544527, 100], [1658544527, 100]...]
                }
            time_range: time range of checking. only error found in this range could be record

        Returns:
            bool
        """
        pass


class BaseMultiItemAlgorithmTwo(metaclass=ABCMeta):
    """
    Base algorithm class. All multi item check algorithm which based on single item check result
    should inherit this class
    """

    @abstractmethod
    def calculate(self, data: dict):
        """
        overload the calculate function
        Args:
            data: result of single item check, like {"cpu_load15": True, "rx_error": False}

        Returns:
            bool
        """
        pass
