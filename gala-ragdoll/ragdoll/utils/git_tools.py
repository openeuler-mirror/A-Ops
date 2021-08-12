import os
import subprocess
import sys
from datetime import datetime
from dateutil.parser import parse
from ragdoll.models.git_log_message import GitLogMessage
from ragdoll.models.conf_base_info import ConfBaseInfo
from ragdoll.controllers.format import Format
from ragdoll import util

class GitTools(object):
    def __init__(self):
        self._target_dir = "/home/confTrace"

    @property
    def target_dir(self):
        return self._target_dir

    @target_dir.setter
    def target_dir(self, target_dir):
        self._target_dir = target_dir

    def gitInit(self):
        cwdDir = os.getcwd()
        os.chdir(self._target_dir)
        shell = "git init"
        returncode = self.run_shell_return_code(shell)
        os.chdir(cwdDir)
        return returncode

    def gitCommit(self, message):
        cwdDir = os.getcwd()
        os.chdir(self._target_dir)
        cmd1 = "git add ."
        returncode1 = self.run_shell_return_code(cmd1)
        if returncode1 == 0:
            cmd2 = "git commit -m '{}'".format(message)
            returncode2 = self.run_shell_return_code(cmd2)
            returncode = returncode2
        else:
                returncode = returncode1
        os.chdir(cwdDir)

        return returncode

    def gitLog(self, path):
        cwdDir = os.getcwd()
        os.chdir(path.rsplit("/", 1)[0])
        print(os.getcwd())
        shell = ['git log {}'.format(path)]
        output = self.run_shell_return_output(shell)
        os.chdir(cwdDir)
        return output

    # 执行shell命令, 并返回执行结果的状态码
    def run_shell_return_code(self, shell):
        cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                            stdout=sys.stdout, universal_newlines=True, shell=True, bufsize=1)

        output, err = cmd.communicate()
        return cmd.returncode

    # 执行shell命令，并返回执行结果和状态码
    def run_shell_return_output(self, shell):
        cmd = subprocess.Popen(shell, stdout=subprocess.PIPE, shell=True)
        print("################# shell cmd ################")
        print("subprocess.Popen({shell}, stdout=subprocess.PIPE, shell=True)".format(shell=shell))
        print("################# shell cmd end ################")
        output, err = cmd.communicate()
        return output


    def makeGitMessage(self, path, logMessage):
        if len(logMessage) == 0:
            return "the logMessage is null"
        print("AAAA path is : {}".format(path))
        cwdDir = os.getcwd()
        os.chdir(path.rsplit("/", 1)[0])
        print(os.getcwd())
        print("logMessage is : {}".format(logMessage))
        gitLogMessageList = []
        singleLogLen = 6
        # message的个数采用count计数
        count = logMessage.count("commit")
        lines = logMessage.split('\n')

        for index in range(0, count):
            print("AAAAAAAAAAAAAAA count is : {}".format(index))
            gitMessage = GitLogMessage()
            for temp in range(0, singleLogLen):
                line = lines[index * singleLogLen + temp]
                value = line.split(" ", 1)[-1]
                if "commit" in line:
                    gitMessage.change_id = value
                if "Author" in line:
                    gitMessage.author = value
                if "Date" in line:
                    gitMessage._date = value[2:]
            print("gitMessage is : {}".format(gitMessage))
            gitMessage.change_reason = lines[index * singleLogLen + 4]
            xpath = path.split('/', 3)[-1]
            gitLogMessageList.append(gitMessage)

        print("################# gitMessage start ################")
        if count == 1:
            last_message = gitLogMessageList[0]
            last_message.post_value = Format.get_file_content_by_read(path)
            os.chdir(cwdDir)
            return gitLogMessageList

        for index in range(0, count - 1):
            message = gitLogMessageList[index]
            next_message = gitLogMessageList[index + 1]
            message.post_value = Format.get_file_content_by_read(path)
            shell = ['git checkout {}'.format(next_message.change_id)]
            output = self.run_shell_return_output(shell)
            message.pre_value = Format.get_file_content_by_read(path)
        # 最后一条changlog
        first_message = gitLogMessageList[count - 1]
        first_message.post_value = Format.get_file_content_by_read(path)

        # 切换回最后的状态
        shell = ['git checkout {}'.format(gitLogMessageList[0].change_id)]
        output = self.run_shell_return_output(shell)
        print("################# gitMessage end ################")
        os.chdir(cwdDir)
        return gitLogMessageList

    def getLogMessageByPath(self, confPath):
        """
        :desc: Returns the Git change record under the current path.
        :param : string
        :rtype: confBaseInfo
        """
        logMessage = self.gitLog(confPath)
        gitMessage = self.makeGitMessage(confPath, logMessage.decode('utf-8'))

        return gitMessage
