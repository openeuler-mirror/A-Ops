from __future__ import absolute_import
import importlib
import json

from ragdoll.config_model.ssh_config import SshConfig
from ragdoll.test import BaseTestCase

BASE_PATH = "ragdoll.config_model."
CONFIG_MODEL_NAME = "Config"
PROJECT_NAME = "_config"
conf_type = "ssh"

conf_info = "# If you want to change the port on a SELinux system, you have to tell\n" \
            "# SELinux about this change.\n" \
            "# semanage port -a -t ssh_port_t -p tcp #PORTNUMBER\n" \
            "#Port 22\n" \
            "#AddressFamily any\n" \
            "#ListenAddress 0.0.0.0\n" \
            "#ListenAddress ::\n" \
            "HostKey /etc/ssh/ssh_host_rsa_key \n" \
            "#HostKey /etc/ssh/ssh_host_ecdsa_key\n" \
            "HostKey /etc/ssh/ssh_host_ed25519_key\n" \
            "SyslogFacility AUTH\n" \
            "PermitRootLogin yes\n" \
            "AuthorizedKeysFile	.ssh/authorized_keys\n" \
            "PasswordAuthentication yes\n" \
            "KbdInteractiveAuthentication no\n" \
            "GSSAPIAuthentication yes\n" \
            "GSSAPICleanupCredentials no\n" \
            "UsePAM yes\n" \
            "X11Forwarding no\n" \
            "PrintMotd no\n" \
            "AcceptEnv LANG LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY LC_MESSAGES\n" \
            "AcceptEnv LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT\n" \
            "AcceptEnv LC_IDENTIFICATION LC_ALL LANGUAGE\n" \
            "AcceptEnv XMODIFIERS\n" \
            "Subsystem sftp /usr/libexec/openssh/sftp-server -l INFO -f AUTH\n" \
            "Ciphers aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com,chacha20-poly1305@openssh.com"

dst_conf = '[\n' \
           '{\n' \
           '"Include": "/etc/ssh/sshd_config.d/*.conf"\n' \
           '},\n' \
           '{\n' \
           '"HostKey": "/etc/ssh/ssh_host_rsa_key"\n' \
           '}\n' \
           ']'
null_conf_info = ""


class TestSshConfig(BaseTestCase):
    def create_conf_model(self):
        conf_model = ""
        project_name = conf_type + PROJECT_NAME  # example: ini_config
        project_path = BASE_PATH + project_name  # example: ragdoll.config_model.ini_config
        model_name = conf_type.capitalize() + CONFIG_MODEL_NAME  # example: IniConfig

        try:
            project = importlib.import_module(project_path)
        except ImportError:
            conf_model = ""
        else:
            _conf_model_class = getattr(project, model_name, None)  # example: IniConfig
            if _conf_model_class:
                conf_model = _conf_model_class()  # example: IniConfig()

        return conf_model

    def test_parse_conf_to_dict(self):
        conf_model = self.create_conf_model()
        conf_dict_list = conf_model._parse_conf_to_dict(conf_info)
        print("conf_dict_list is: {}".format(conf_dict_list))
        self.assertEqual(len(conf_dict_list), 18)

    def test_read_conf_null(self):
        conf_model = self.create_conf_model()
        conf_model.read_conf(null_conf_info)
        self.assertEqual(len(conf_model.conf), 0)

    def test_conf_compare(self):
        conf_model = self.create_conf_model()
        conf_dict_list = conf_model._parse_conf_to_dict(conf_info)
        res = conf_model.conf_compare(dst_conf, json.dumps(conf_dict_list))

        print("res is: {}".format(res))
        self.assertEqual(res, "NOT SYNCHRONIZE")

    def test_write_conf(self):
        sshConfig = SshConfig()
        conf_model = self.create_conf_model()
        conf_dict_list = conf_model._parse_conf_to_dict(conf_info)
        sshConfig.conf = conf_dict_list
        content = conf_model.write_conf(spacer_info="")
        self.assertTrue(len(content) > 0)


if __name__ == '__main__':
    import unittest

    unittest.main()
