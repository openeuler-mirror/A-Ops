# !/usr/bin/python3
# coding: utf-8
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
import os
import unittest
import shutil
from aops_manager.deploy_manager.utils import build_yaml, make_dir, copy_dirs, move_file

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class TestUtils(unittest.TestCase):
    def test_build_yaml(self):
        test_yaml = {"group": {"host1": "1.1.1.1", "host2": "2.2.2.2"}}
        file_path = os.path.join(CURRENT_PATH, "test.yml")
        build_yaml(file_path, test_yaml)
        self.assertTrue(os.path.exists(file_path), msg="Build yaml file")
        os.remove(file_path)

    def test_make_dir(self):
        with self.assertRaises(ValueError, msg="dir is None exception."):
            make_dir(None)

        file_path = os.path.join(CURRENT_PATH, "tmp")
        make_dir(file_path)
        self.assertTrue(os.path.exists(file_path), msg="make dir while dst is not existed")

        make_dir(file_path)
        self.assertTrue(os.path.exists(file_path), msg="make dir while dst is existed")
        shutil.rmtree(file_path)

    @staticmethod
    def prepare_dirs():
        src_path = os.path.join(CURRENT_PATH, "src")
        src_file_path = os.path.join(CURRENT_PATH, "src", "test1")
        os.makedirs(src_path)
        with open(src_file_path, "w", encoding='utf-8') as file_obj:
            file_obj.write("qqqqq")

        children_path = os.path.join(CURRENT_PATH, "src", "child")
        children_file_path = os.path.join(children_path, "test2")
        os.makedirs(children_path)
        with open(children_file_path, "w", encoding='utf-8') as file_obj:
            file_obj.write("wwwww")

    def test_copy_dirs(self):
        with self.assertRaises(ValueError, msg="dir is None exception."):
            copy_dirs(None, None)

        src_path = os.path.join(CURRENT_PATH, "src")
        dst_path = os.path.join(CURRENT_PATH, "dst")
        dst_file_path = os.path.join(CURRENT_PATH, "dst", "test1")
        dst_child_file_path = os.path.join(CURRENT_PATH, "dst", "child", "test2")
        self.prepare_dirs()

        copy_dirs(src_path, dst_path)
        self.assertTrue(os.path.exists(dst_file_path), msg="Copy dir to an empty dir")
        self.assertTrue(os.path.exists(dst_child_file_path), msg="Copy child dir to an empty dir")

        copy_dirs(src_path, dst_path)
        self.assertTrue(os.path.exists(dst_file_path), msg="Copy dir to a not empty dir")
        self.assertTrue(os.path.exists(dst_child_file_path),
                        msg="Copy child dir to a not empty dir")
        shutil.rmtree(dst_path)
        shutil.rmtree(src_path)

    def test_move_file(self):
        with self.assertRaises(ValueError, msg="dir is None exception."):
            copy_dirs(None, None)

        src_path = os.path.join(CURRENT_PATH, "src")
        src_file_path = os.path.join(CURRENT_PATH, "src", "test1")
        dst_path = os.path.join(CURRENT_PATH, "dst")
        os.makedirs(src_path)
        with open(src_file_path, "w") as file_obj:
            file_obj.write("qqqqq")

        dst_file_path = os.path.join(dst_path, "test1")
        move_file(src_path, dst_path, "test1")
        self.assertTrue(os.path.exists(dst_file_path), msg="Move file to dst")
        self.assertFalse(os.path.exists(src_file_path), msg="Move file to dst, src is delete")

        self.assertTrue(os.path.exists(dst_file_path), msg="Move file to dst, if dst is existed")
        self.assertFalse(os.path.exists(src_file_path), msg="Move file to dst, src is delete")
        shutil.rmtree(src_path)
        shutil.rmtree(dst_path)


if __name__ == "__main__":
    unittest.main()
