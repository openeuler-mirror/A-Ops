import os

from ragdoll.utils.git_tools import GitTools

class Prepare(object):
    def __init__(self):
        self._target_dir = "/home/confTrace"

    @property
    def target_dir(self):
        return self._target_dir

    @target_dir.setter
    def target_dir(self, target_dir):
        self._target_dir = target_dir

    def mdkir_git_warehose(self):
        res = True
        if os.path.exists(self._target_dir):
            rest = self.git_init()
            return rest
        cmd1 = "mkdir -p {}".format(self._target_dir)
        git_tools = GitTools()
        mkdir_code = git_tools.run_shell_return_code(cmd1)
        git_code = self.git_init()
        if mkdir_code != 0 or git_code != 0:
            res = False
        return res

    def git_init(self):
        res = False
        cwd = os.getcwd()
        os.chdir(self._target_dir)
        git_tools = GitTools()
        init_code = git_tools.gitInit()
        if init_code == 0:
                res = True
        os.chdir(cwd)
        return res
