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
import unittest

from aops_check.core.experiment.app import App


class TestApp(unittest.TestCase):
    def test_load_models_for_default_should_return_all_model_when_input_correct_model_info(self):
        mock_model_info = {'Ewma-1': {}, 'Mae-1': {}}
        app = App()
        app.load_models(model_info=mock_model_info, default_mode=True)
        self.assertEqual(mock_model_info.keys(), app.model.keys())

    def test_load_models_for_default_should_return_partial_model_when_part_of_input_model_info_is_correct(self):
        mock_model_info = {'Ewma-1': {}, 'Mae-1': {}, 'test': {}}
        app = App()
        app.load_models(model_info=mock_model_info, default_mode=True)
        mock_model_info.pop('test')
        self.assertEqual(mock_model_info.keys(), app.model.keys())

    def test_load_models_for_default_should_return_empty_model_when_part_of_input_incorrect_model_info(self):
        mock_model_info = {'Ewma': {}, 'Mae': {}, 'test': {}}
        app = App()
        app.load_models(model_info=mock_model_info, default_mode=True)
        self.assertEqual({}, app.model)

    def test_load_models_for_default_should_return_empty_model_when_input_is_null(self):
        mock_model_info = {}
        app = App()
        app.load_models(model_info=mock_model_info, default_mode=True)
        self.assertEqual({}, app.model)