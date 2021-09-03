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
import shutil
import unittest
from aops_manager.deploy_manager.ansible_runner.inventory_builder import InventoryBuilder
from aops_manager.deploy_manager.config import HOST_VARS_PATH, INVENTORY_PATH, PLAYBOOK_VARS_PATH

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class TestInventoryBuilder(unittest.TestCase):
    output_path = "output"

    def test_add_host_vars(self):
        inventory_builder = InventoryBuilder()
        inventory_builder._add_host_vars("host1", "ip", "127.0.0.1", False)
        self.assertDictEqual(inventory_builder._host_vars,
                             {"host1": {"ip": "127.0.0.1"}},
                             msg="Adding variables to host_vars")
        self.assertDictEqual(inventory_builder._vault_host_vars, {},
                             msg="Variables are not added to host_vars.")

        inventory_builder._add_host_vars("host1", "pwd", "12345", True)
        self.assertDictEqual(inventory_builder._host_vars,
                             {"host1": {"ip": "127.0.0.1", "pwd": "{{vault_pwd}}"}},
                             msg="Adding variables to host_vars")
        self.assertDictEqual(inventory_builder._vault_host_vars,
                             {"host1": {"vault_pwd": "12345"}},
                             msg="Variables are not added to host_vars.")

    def test_dump_host_vars(self):
        inventory_builder = InventoryBuilder()
        inventory_builder._add_host_vars("host1", "ip", "127.0.0.1", False)
        inventory_builder._add_host_vars("host1", "pwd", "12345", True)
        inventory_builder._dump_host_vars("54321", TestInventoryBuilder.output_path)

        plain_file_path = os.path.join(CURRENT_PATH,
                                       TestInventoryBuilder.output_path,
                                       "host_vars", "host1", "plain")
        self.assertTrue(os.path.exists(plain_file_path), msg="dump plain file")
        crypted_file_path = os.path.join(CURRENT_PATH,
                                         TestInventoryBuilder.output_path,
                                         "host_vars", "host1", "crypted")
        self.assertTrue(os.path.exists(crypted_file_path), msg="dump crypted file")

        shutil.rmtree(os.path.join(CURRENT_PATH, TestInventoryBuilder.output_path))

    def test_move_vars_to_inventory(self):
        inventory_builder = InventoryBuilder()
        inventory_builder._add_host_vars("host1", "ip", "127.0.0.1", False)
        inventory_builder._add_host_vars("host1", "pwd", "12345", True)
        inventory_builder._dump_host_vars("54321", TestInventoryBuilder.output_path)
        src_path = os.path.join(CURRENT_PATH,
                                TestInventoryBuilder.output_path,
                                "host_vars")

        with self.assertRaises(ValueError, msg="Invalid parameters"):
            inventory_builder.move_host_vars_to_inventory(None, None)

        inventory_builder.move_host_vars_to_inventory(src_path, "host1")
        plain_file_path = os.path.join(HOST_VARS_PATH, "host1", "plain")
        self.assertTrue(os.path.exists(plain_file_path), msg="move plain file")
        crypted_file_path = os.path.join(HOST_VARS_PATH, "host1", "crypted")
        self.assertTrue(os.path.exists(crypted_file_path), msg="move crypted file")
        shutil.rmtree(os.path.join(CURRENT_PATH, TestInventoryBuilder.output_path))
        shutil.rmtree(HOST_VARS_PATH)

    def test_import_host_list(self):
        inventory_builder = InventoryBuilder()
        with self.assertRaises(ValueError, msg="Invalid parameters"):
            inventory_builder.import_host_list({}, None, None)

        host_list_json = {
            "group_info": {
                "host_name": {
                    "ansible_host": "192.168.1.1",
                    "var1": "value1",
                    "var2": "value2"
                }
            }
        }

        inventory_builder.import_host_list(host_list_json,
                                           "host_name",
                                           TestInventoryBuilder.output_path)
        host_file_path = os.path.join(CURRENT_PATH,
                                      TestInventoryBuilder.output_path,
                                      "host_name")
        self.assertTrue(os.path.exists(host_file_path), msg="import_host_list")
        shutil.rmtree(os.path.join(CURRENT_PATH, TestInventoryBuilder.output_path))

    def test_move_host_to_inventory(self):
        host_list_json = {
            "group_info": {
                "host_name": {
                    "ansible_host": "192.168.1.1",
                    "var1": "value1",
                    "var2": "value2"
                }
            }
        }
        inventory_builder = InventoryBuilder()
        inventory_builder.import_host_list(host_list_json, "test", TestInventoryBuilder.output_path)
        src_path = os.path.join(CURRENT_PATH, TestInventoryBuilder.output_path)

        with self.assertRaises(ValueError, msg="Invalid parameters"):
            inventory_builder.move_host_to_inventory(None, None)

        inventory_builder.move_host_to_inventory(src_path, "test")
        plain_file_path = os.path.join(INVENTORY_PATH, "test")
        self.assertTrue(os.path.exists(plain_file_path), msg="move host file")

    def test_move_playbooks_vars_to_inventory(self):
        with open("playbook_vars.yml", "w") as test_file:
            test_file.write("XXX")

        inventory_builder = InventoryBuilder()

        with self.assertRaises(ValueError, msg="Invalid parameters"):
            inventory_builder.move_host_to_inventory(None, None)

        inventory_builder.move_playbook_vars_to_inventory(".", "playbook_vars.yml")
        playbook_vars_file_path = os.path.join(PLAYBOOK_VARS_PATH, "playbook_vars.yml")
        self.assertTrue(os.path.exists(playbook_vars_file_path), msg="move host file")
        os.remove(playbook_vars_file_path)

    def test_import_host_vars(self):
        inventory_builder = InventoryBuilder()
        with self.assertRaises(ValueError, msg="Invalid parameters"):
            inventory_builder.import_host_vars({}, None, None)

        var_list_json = {
            "group_info": {
                "host_name": {
                    "ansible_user": "aops",
                    "ansible_ssh_pass": "123",
                    "ansible_become_user": "root",
                    "ansible_become_method": "su",
                    "ansible_become_password": "456"
                }
            }
        }

        inventory_builder.import_host_vars(var_list_json,
                                           "123456",
                                           TestInventoryBuilder.output_path)
        plain_file_path = os.path.join(CURRENT_PATH,
                                       TestInventoryBuilder.output_path,
                                       "host_vars", "host_name", "plain")
        self.assertTrue(os.path.exists(plain_file_path), msg="host vars plain file existed")
        crypted_file_path = os.path.join(CURRENT_PATH,
                                         TestInventoryBuilder.output_path,
                                         "host_vars", "host_name", "crypted")
        self.assertTrue(os.path.exists(crypted_file_path), msg="host vars crypted file existed")
        shutil.rmtree(os.path.join(CURRENT_PATH, TestInventoryBuilder.output_path))

    def test_remove_host_vars_in_inventory(self):
        self.assertFalse(os.path.exists(HOST_VARS_PATH), msg="host_vars is not existed")
        InventoryBuilder.remove_host_vars_in_inventory()
        self.assertFalse(os.path.exists(HOST_VARS_PATH),
                         msg="If host_vars not existed no need to remove")

        inventory_builder = InventoryBuilder()
        inventory_builder._add_host_vars("host1", "ip", "127.0.0.1", False)
        inventory_builder._add_host_vars("host1", "pwd", "12345", True)
        inventory_builder._dump_host_vars("54321", TestInventoryBuilder.output_path)
        src_path = os.path.join(CURRENT_PATH,
                                TestInventoryBuilder.output_path,
                                "host_vars")
        inventory_builder.move_host_vars_to_inventory(src_path, "host1")
        self.assertTrue(os.path.exists(HOST_VARS_PATH), msg="host_vars is existed")
        inventory_builder.remove_host_vars_in_inventory()
        self.assertFalse(os.path.exists(HOST_VARS_PATH), msg="host_vars has benn deleted")


if __name__ == "__main__":
    unittest.main()
