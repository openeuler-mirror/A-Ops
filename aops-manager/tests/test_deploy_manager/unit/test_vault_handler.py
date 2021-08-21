# !/usr/bin/python3
# coding: utf-8
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import unittest
from aops_manager.deploy_manager.ansible_runner.vault_handler import VaultHandler
from ansible.parsing.dataloader import DataLoader


class TestVaultHandler(unittest.TestCase):
    def test_encrypt_string(self):
        vault_handler = VaultHandler("12345")
        self.assertEqual(vault_handler.encrypt_string(""), "")
        self.assertEqual(vault_handler.encrypt_string(None), "")

        plain_txt = "qqqqqqq"
        crypted_txt = vault_handler.encrypt_string(plain_txt)
        self.assertNotEqual(plain_txt, crypted_txt, "Sensitive information is invisible.")

    def test_setup_vault_secrets(self):
        with self.assertRaises(ValueError, msg="Data loader is None"):
            VaultHandler.setup_vault_secrets(None, vault_password="12345")

        self.assertListEqual(VaultHandler.setup_vault_secrets(DataLoader(),
                                                              vault_password=""), [],
                             msg="Invalid vault_password")

        vault_secrets = VaultHandler.setup_vault_secrets(DataLoader(),
                                                         vault_password="12345")
        self.assertEqual(vault_secrets[0][0], "default")

        vault_secrets = VaultHandler.setup_vault_secrets(DataLoader(),
                                                         vault_password="12345")
        self.assertEqual(vault_secrets[0][0], "default")

    def test_get_prompt_vault_secret(self):
        vault_id_name = "test"
        vault_password = "123456"
        vault_secrets = []
        loader = DataLoader()
        VaultHandler._get_prompt_vault_secret(vault_id_name, vault_password, vault_secrets, loader)
        self.assertEqual(vault_secrets[0][0], "test", msg="Get vault secret succeed.")


if __name__ == "__main__":
    unittest.main()
