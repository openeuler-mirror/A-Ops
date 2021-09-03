#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Author: YangYunYi
Date: 2021/9/2 15:53
docs: test_all.py
description:
"""
import unittest
import HtmlTestRunner
import os
import coverage
import sys
import time
from aops_utils.log.log import LOGGER

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
suite = unittest.TestSuite()


def build_test_suite():
    """
    Build total test suite
    Returns:
        None

    """
    all_cases = unittest.defaultTestLoader.discover('.', 'test_*.py')
    for case in all_cases:
        suite.addTests(case)


def get_time():
    """
    get time str
    Returns:
        formatted time

    """
    return time.strftime('%Y-%m-%d %H_%M_%S', time.localtime(time.time()))


def get_html_pass_report():
    """
    Get pass report
    Returns:
        None

    """
    build_test_suite()
    file_dir = os.path.join(CURRENT_PATH, "pass_report")
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    report_name = "pass_report_{}".format(get_time())
    runner = HtmlTestRunner.HTMLTestRunner(file_dir,
                                           report_title="Passing rate",
                                           combine_reports=True,
                                           report_name=report_name)
    runner.run(suite)
    LOGGER.info("get_html_pass_report succeed")


def get_coverage_report():
    """
    get coverage report
    Returns:
        None

    """
    # 实例化对象
    cov = coverage.coverage()
    # 开始分析
    cov.start()
    get_html_pass_report()
    # 结束分析
    cov.stop()
    # 结果保存
    cov.save()
    # 命令行模式展示结果
    cov.report()
    # 生成HTML覆盖率报告
    cov.html_report(directory='cov_report')


def main():
    """
    main func
    Returns:
        None

    """
    test_mode = "pass_report"
    if len(sys.argv) == 2:
        para = sys.argv[1]
        if para == "cov":
            test_mode = "cov_report"

    if test_mode == "pass_report":
        get_html_pass_report()
    elif test_mode == "cov_report":
        get_coverage_report()


if __name__ == "__main__":
    main()
