import os
import subprocess
import sys
from datetime import datetime
from dateutil.parser import parse
from swagger_server.models.git_log_message import GitLogMessage
from swagger_server.models.conf_base_info import ConfBaseInfo
from swagger_server import util

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

        cwdDir = os.getcwd()
        os.chdir(path.rsplit("/", 1)[0])
        print(os.getcwd())

        count = logMessage.count("commit")
        lines = logMessage.split('\n')
        gitLogMessageList = []
        singleLogLen = 6

        print("len(lines) is : {}".format(len(lines)))
        print("(int(len(lines) / singleLogLen) - 1) is : {}".format((int(len(lines) / singleLogLen) - 1)))
        for count in range(0, (int(len(lines) / singleLogLen))):
            print("AAAAAAAAAAAAAAA count is : {}".format(count))
            gitMessage = GitLogMessage()
            for temp in range(0, 6):
                line = lines[count * singleLogLen + temp]
                value = line.split(" ", 1)[-1]
                if "commit" in line:
                    gitMessage.change_id = value
                if "Author" in line:
                    gitMessage.author = value
                if "Date" in line:
                    gitMessage._date = value[2:]
            print("gitMessage is : {}".format(gitMessage))
            gitMessage.change_reason = lines[count * singleLogLen + 4]
            xpath = path.split('/', 3)[-1]
            preValue, postValue = self.getExpectValue(gitMessage.change_id, xpath)
            gitMessage.pre_value = preValue
            gitMessage.post_value = postValue
            gitLogMessageList.append(gitMessage)
            # print("################# gitMessage start ################")
            # print("gitMessage is : {}".format(gitMessage))
            # print("################# gitMessage end ################")

        os.chdir(cwdDir)
        return gitLogMessageList

    def getExpectValue(self, changeId, xpath):
        """
        desc：Get the corresponding expected value based on XPath and ChangeID
        """
        shell = ['git show {}'.format(changeId)]
        output = self.run_shell_return_output(shell)
        message = output.decode('utf-8').split('diff')
        print("xpath is : {}".format(xpath))
        print("message is : {}".format(message))
        for temp in message:
            if xpath in temp:
                print("temp is : {}".format(temp))
                singleMessage = temp.split('\n')
                preValue= ""
                preValueString = singleMessage[len(singleMessage) - 3].split('-')[-1]
                if "@@" not in preValueString:
                    preValue = preValueString
                print("singleMessage is : {}".format(singleMessage))
                postValue = singleMessage[len(singleMessage) - 2].split('+')[-1]

        return preValue, postValue

    def getLogMessageByPath(self, confPath):
        """
        :desc: Returns the Git change record under the current path.
        :param : string
        :rtype: confBaseInfo
        """
        logMessage = self.gitLog(confPath)
        gitMessage = self.makeGitMessage(confPath, logMessage.decode('utf-8'))

        return gitMessage
