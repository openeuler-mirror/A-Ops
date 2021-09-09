import os
import subprocess
import sys
import configparser
import ast
from datetime import datetime
from dateutil.parser import parse
from ragdoll.models.git_log_message import GitLogMessage
from ragdoll.models.conf_base_info import ConfBaseInfo
from ragdoll.controllers.format import Format
from ragdoll import util

CONFIG = "/etc/ragdoll/gala-ragdoll.conf"

class GitTools(object):
    def __init__(self, target_dir = None):
        if target_dir:
            self._target_dir = target_dir
        else:
            self._target_dir = self.load_git_dir()

    def load_git_dir(self):
        cf = configparser.ConfigParser()
        cf = configparser.ConfigParser()
        if os.path.exists(CONFIG):
            cf.read(CONFIG, encoding="utf-8")
        else:
            parent = os.path.dirname(os.path.realpath(__file__))
            conf_path = os.path.join(parent, "../../config/gala-ragdoll.conf")
            cf.read(conf_path, encoding="utf-8")
        git_dir = ast.literal_eval(cf.get("git", "git_dir"))
        return git_dir

    @property
    def target_dir(self):
        return self.load_git_dir()

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

    def git_create_user(self, username, useremail):
        """
        desc: Git initial configuration about add a user name and email
        """
        returncode = 1
        cmd_add_user_name = "git config user.name {}".format(username)
        gitTools = GitTools()
        cmd_name_code = gitTools.run_shell_return_code(cmd_add_user_name)
        cmd_add_user_email = "git config user.email {}".format(useremail)
        cmd_email_code = gitTools.run_shell_return_code(cmd_add_user_email)
        if cmd_name_code and cmd_email_code:
            returncode = 0
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
        os.chdir(self._target_dir)
        shell = ['git log {}'.format(path)]
        output = self.run_shell_return_output(shell)
        os.chdir(cwdDir)
        return output

    # Execute the shell command and return the execution node
    def run_shell_return_code(self, shell):
        cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                            stdout=sys.stdout, universal_newlines=True, shell=True, bufsize=1)

        output, err = cmd.communicate()
        return cmd.returncode

    # Execute the shell command and return the execution node and output
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
        os.chdir(self._target_dir)
        print(os.getcwd())
        print("logMessage is : {}".format(logMessage))
        gitLogMessageList = []
        singleLogLen = 6
        # the count is num of message
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
            gitMessage.change_reason = lines[index * singleLogLen + 4]
            print("gitMessage is : {}".format(gitMessage))
            gitLogMessageList.append(gitMessage)

        print("################# gitMessage start ################")
        if count == 1:
            last_message = gitLogMessageList[0]
            last_message.post_value = Format.get_file_content_by_read(path)
            os.chdir(cwdDir)
            return gitLogMessageList

        for index in range(0, count - 1):
            print("index is : {}".format(index))
            message = gitLogMessageList[index]
            next_message = gitLogMessageList[index + 1]
            message.post_value = Format.get_file_content_by_read(path)
            shell = ['git checkout {}'.format(next_message.change_id)]
            output = self.run_shell_return_output(shell)
            message.pre_value = Format.get_file_content_by_read(path)
        # the last changlog
        first_message = gitLogMessageList[count - 1]
        first_message.post_value = Format.get_file_content_by_read(path)

        print("################# gitMessage end ################")
        os.chdir(cwdDir)
        return gitLogMessageList

    def gitCheckToHead(self):
        """
        desc: git checkout to the HEAD in this git.
        """
        cwdDir = os.getcwd()
        os.chdir(self._target_dir)
        cmd = ['git checkout master']
        output = self.run_shell_return_code(cmd)
        os.chdir(cwdDir)
        return output

    def getLogMessageByPath(self, confPath):
        """
        :desc: Returns the Git change record under the current path.
        :param : string
        :rtype: confBaseInfo
        """
        logMessage = self.gitLog(confPath)
        gitMessage = self.makeGitMessage(confPath, logMessage.decode('utf-8'))
        checoutResult = self.gitCheckToHead()
        return gitMessage
