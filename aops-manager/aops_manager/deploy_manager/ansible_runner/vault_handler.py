# coding: utf-8
# !/usr/bin/python3
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
Description: Ansible Vault Encryption Processing
Class: VaultHandler
"""
from ansible import constants as Constants
from ansible.constants import DEFAULT_VAULT_ID_MATCH
from ansible.parsing.vault import VaultLib
from ansible.parsing.vault import VaultSecret
from ansible.parsing.vault import PromptVaultSecret
from aops_utils.log.log import LOGGER


class VaultHandler:
    """
    Ansible Vault Encryption Processing
    """

    def __init__(self, vault_password):
        """
        Construct Function
        Args:
            vault_password (str): vault encrypted password
        """
        self._vault = VaultLib(
            [(DEFAULT_VAULT_ID_MATCH, VaultSecret(bytes(vault_password, encoding="utf8")))])

    def encrypt_string(self, plaintext):
        """
        Encrypt a character string.
        Args:
            plaintext (str): Plaintext character string

        Returns:
            Ciphertext character string

        """
        if not plaintext:
            LOGGER.error("The plaintext is null.")
            return ""
        return self._vault.encrypt(bytes(plaintext, encoding="utf8"))

    @staticmethod
    def _get_prompt_vault_secret(vault_id_name, vault_password, vault_secrets, loader):
        """
        Obtains the vault password entered in real time.
        Args:
            vault_id_name (str): vault id name
            vault_password (str): vault password
            vault_secrets (list): vault secrets object
            loader (DataLoader): data loader

        Returns:
            None

        """
        built_vault_id = vault_id_name or Constants.DEFAULT_VAULT_IDENTITY

        prompted_vault_secret = PromptVaultSecret(_bytes=bytes(vault_password,
                                                               encoding="utf8"),
                                                  vault_id=built_vault_id)

        vault_secrets.append((built_vault_id, prompted_vault_secret))

        # update loader with new secrets incrementally, so we can load a vault password
        # that is encrypted with a vault secret provided earlier
        loader.set_vault_secrets(vault_secrets)

    @staticmethod
    def setup_vault_secrets(loader, vault_password=None):
        """
        Setting the vault password
        Args:
            loader (DataLoader): data loader
            vault_password (str): vault password

        Returns:
            None

        Raise:
            ValueError
        """
        if not loader:
            raise ValueError("Data loader is None")

        # list of tuples
        vault_secrets = []

        if vault_password:
            VaultHandler._get_prompt_vault_secret("default",
                                                  vault_password,
                                                  vault_secrets,
                                                  loader)
            LOGGER.debug("get_prompt_vault_secret")
        return vault_secrets
