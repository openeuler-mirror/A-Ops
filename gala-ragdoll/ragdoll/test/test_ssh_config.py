from __future__ import absolute_import
import importlib
import json

from ragdoll.config_model.ssh_config import SshConfig
from ragdoll.test import BaseTestCase

BASE_PATH = "ragdoll.config_model."
CONFIG_MODEL_NAME = "Config"
PROJECT_NAME = "_config"
CONF_TYPE = "ssh"

CONF_INFO = "# If you want to change the port on a SELinux system, you have to tell\n" \
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
 \
DST_CONF = '[\n' \
           '{\n' \
           '"Include": "/etc/ssh/sshd_config.d/*.conf"\n' \
           '},\n' \
           '{\n' \
           '"HostKey": "/etc/ssh/ssh_host_rsa_key"\n' \
           '}\n' \
           ']'
NULL_CONF_INFO = ""


class TestSshConfig(BaseTestCase):
    def create_conf_model(self):
        conf_model = ""
        project_name = CONF_TYPE + PROJECT_NAME  # example: ini_config
        project_path = BASE_PATH + project_name  # example: ragdoll.config_model.ini_config
        model_name = CONF_TYPE.capitalize() + CONFIG_MODEL_NAME  # example: IniConfig

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
        conf_dict_list = conf_model.parse_conf_to_dict(CONF_INFO)
        self.assertEqual(len(conf_dict_list), 17)

    def test_read_conf_null(self):
        conf_model = self.create_conf_model()
        conf_model.read_conf(NULL_CONF_INFO)
        self.assertEqual(len(conf_model.conf), 0)

    def test_conf_compare(self):
        conf_model = self.create_conf_model()
        conf_dict_list = conf_model.parse_conf_to_dict(CONF_INFO)
        res = conf_model.conf_compare(DST_CONF, json.dumps(conf_dict_list))

        self.assertEqual(res, "NOT SYNCHRONIZE")

    def test_write_conf(self):
        ssh_config = SshConfig()
        conf_model = self.create_conf_model()
        conf_dict_list = conf_model.parse_conf_to_dict(CONF_INFO)
        ssh_config.conf = conf_dict_list
        content = conf_model.write_conf(spacer_info="")
        self.assertTrue(len(content) > 0)


if __name__ == '__main__':
    import unittest

    unittest.main()
