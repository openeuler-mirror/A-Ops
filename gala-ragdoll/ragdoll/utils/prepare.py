import os

from ragdoll.utils.git_tools import GitTools

class Prepare(object):
    def __init__(self, target_dir):
        self._target_dir = target_dir

    @property
    def target_dir(self):
        return self._target_dir

    @target_dir.setter
    def target_dir(self, target_dir):
        self._target_dir = target_dir

    def mdkir_git_warehose(self, username, useremail):
        res = True
        print("self._target_dir is : {}".format(self._target_dir))
        if os.path.exists(self._target_dir):
            rest = self.git_init(username, useremail)
            return rest
        os.umask(0o077)
        cmd1 = "mkdir -p {}".format(self._target_dir)
        git_tools = GitTools(self._target_dir)
        mkdir_code = git_tools.run_shell_return_code(cmd1)
        git_code = self.git_init(username, useremail)
        if mkdir_code != 0:
            res = False
        return res

    def git_init(self, username, useremail):
        res = False
        cwd = os.getcwd()
        os.chdir(self._target_dir)
        git_tools = GitTools(self._target_dir)
        res_init = git_tools.gitInit()
        res_user = git_tools.git_create_user(username, useremail)
        if res_init == 0 and res_user == 0:
            res = True
        os.chdir(cwd)
        return res
