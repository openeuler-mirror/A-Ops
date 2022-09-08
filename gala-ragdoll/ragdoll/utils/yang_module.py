import libyang
import os
import sys
import importlib
import operator
from ragdoll.utils.git_tools import GitTools

PROJECTNAME = "gala-ragdoll"
TARGETDIR = GitTools().target_dir

class YangModule(object):
    def __init__(self):
        self._cwd_dir = os.getcwd()
        self._target_dir = "yang_modules"
        self._ctx = libyang.Context()
        self._yang_dir = self.get_yang_path_in_ragdoll()
        print("_yang_dir is : {}".format(self._yang_dir))
        self._module_list = self.loadYangModules()

    @property
    def target_dir(self):
        return self._target_dir

    @target_dir.setter
    def target_dir(self, value):
        self._target_dir = value

    @property
    def cwd_dir(self):
        return self._cwd_dir

    @cwd_dir.setter
    def cwd_dir(self, cwd_dir):
        self._cwd_dir = cwd_dir

    @property
    def ctx(self):
        return self._ctx

    @ctx.setter
    def ctx(self, ctx):
        self._ctx = ctx

    @property
    def yang_dir(self):
        return self._yang_dir

    @yang_dir.setter
    def yang_dir(self, yang_dir):
        self._yang_dir = yang_dir

    @property
    def module_list(self):
        return self._module_list

    @module_list.setter
    def module_list(self, module_list):
        self._module_list = module_list

    def get_yang_path_in_ragdoll(self):
        """
        desc: get the path of the yang project in 
        """
        paths = self._cwd_dir.split("/")
        print("paths is : {}".format(paths))
        yang_dir = ""
        if PROJECTNAME in paths:
            yang_path = ""
            index = paths.index(PROJECTNAME)
            for d_index in range(1, index + 1):
                yang_path = yang_path + "/" + paths[d_index]
            yang_dir = os.path.join(yang_path, self._target_dir)
        else:
            cmd = "rpm -ql {} | grep {}".format("python3-gala-ragdoll", "yang_modules")
            git_tools = GitTools()
            ls_res = git_tools.run_shell_return_output(cmd).decode().split('\n')
            for d_res in ls_res:
                if d_res.split("/")[-1] == "yang_modules":
                    yang_dir = d_res
                    break
        return yang_dir

    def loadYangModules(self):
        """
        desc: load the yang modules in the path of ../../yang_modules
        """
        module_list = []
        if not self._yang_dir:
            return False
        for root, dirs, files in os.walk(self._yang_dir):
            for d_file in files:
                files_tail = d_file.split('.')[-1]
                if files_tail != "yang":
                    continue
                modulePath = os.path.join(self._yang_dir, d_file)
                # grammar_res = self.check_yang_grammar(modulePath)
                # print("grammar_res is : {}".format(grammar_res))
                # if not grammar_res:
                #     continue
                fo = open(modulePath, 'r+')
                module = self._ctx.parse_module_file(fo)
                module_list.append(module)
                fo.close()
        return module_list

    def getXpathInModule(self, modules):
        """
        desc: return a list as a XpathList:
        module example:
            module: openEuler-logos-openEuler.repo
              +--rw yum
                  +--rw openEuler.repo
                      +--rw section* [name]
                        +--rw name        string
                        +--rw baseurl?    string
                        +--rw gpgcheck?   string
                        +--rw gpgkey?     string
        return exmaple:
            [
                'yum/openEuler.repo/section/name'
                'yum/openEuler.repo/section/baseurl',
                'yum/openEuler.repo/section/enabled',
                'yum/openEuler.repo/section/gpgcheck'
            ]
        Solution: Since there are two Spaces for the first layer of nodes, and three 
        Spaces are added for each additional layer of nodes, Spaces are used to 
        determine the number of layers.
            The number of Spaces before '+--rw' is subtracted by 2 divided by 3 to 
            determine the level
        """
        xpath=[]
        level = []
        init_index = 0
        tree_node = modules.print_mem()
        tree_lines = tree_node.splitlines()
        len_tree = len(tree_lines)
        path = ""
        # The quotient of (node-2) / 3 can be used as the hierarchical value
        for count in range(0, len_tree):
            line = tree_lines[count]
            if not len(line) or line.startswith('module'):
                continue
            tree_split = line.split(' ')
            index = tree_split.index('+--rw')
            index_next = tree_split[index + 1]
            if not index_next[len(index_next) - 1].isalpha():
                index_next = index_next[0: len(index_next) - 1]
            if index == init_index:
                prePath = ""
                for count_temp in range(0, len(level) - 1):
                    prePath += level[count_temp] + '/'
                path = prePath + index_next
                preLevel = level[len(level) - 1]
                level = level[0: len(level) - 1]
                if len(xpath) > 0:
                    last = xpath[len(xpath) - 1]
                    if last[len(last) - 1] is '/':
                        xpath[len(xpath) - 1] = last[0: len(last) - 1]
                    level.append(index_next)
                    xpath.append(path)
                    continue
                else:
                    level.append(index_next)
                    firstPath = prePath + preLevel
                    xpath.append(firstPath)
            elif index > init_index:
                path += index_next + '/'
                init_index = index
                level.append(index_next)
                if len(level) > 3:
                    path = ""
                    for d_level in level:
                        path = path + d_level + "/"
                    xpath.append(path)
                continue
            else:
                level_num = int((index - 2) / 3)
                level = level[0:level_num]
                init_index = index
                level.append(index_next)
                continue
            xpath.append(path)

        # print("xpath is : {}".format(xpath))
        return xpath

    def getFeatureInModule(self, modules):
        """
        desc: return feature information about module.
              We only need the first two layers of module structure, 
              because the first layer is the feature information of the configuration file, 
              and the second layer is the name of the configuration file.
        example:
            input:
                module: openEuler-logos-openEuler.repo
                +--rw yum
                    +--rw openEuler.repo
                        +--rw section* [name]
                            +--rw name        string
                            +--rw baseurl?    string
                            +--rw gpgcheck?   string
                            +--rw gpgkey?     string
            output:
                [yum, openEuler.repo]
        """
        featrueList = []
        tree_node = modules.print_mem()
        tree_lines = tree_node.splitlines()
        # Only the second and third rows need to be retrieved from the module tree
        for count in range(0, 3):
            line = tree_lines[count]
            if not len(line) or line.startswith('module'):
                continue
            tree_split = line.split(' ')
            index = tree_split.index('+--rw')
            index_next = tree_split[index + 1]
            featrueList.append(index_next)

        return featrueList

    def getModuleByFeature(self, feature_path):
        """
        desc: return a module according the feature path.
        example:
            input: yum/openEuler.repo
            output: openEuler-logos-openEuler.repo.yang
        """
        if len(self._module_list) == 0:
            self.loadYangModules()
        feature_paths = feature_path.split('/')
        res_module = None
        if len(self._module_list) > 0:
            for d_module in self._module_list:
                feature_list = self.getFeatureInModule(d_module)
                res = operator.eq(sorted(feature_paths), sorted(feature_list))
                if res:
                    res_module = d_module
                    break
        return res_module

    def getFilePathInModdule(self, modules):
        """
        desc: Return the PATH content of the extension tag in the module
        emaple:
            input: module:openEuler-logos-openEuler.repo
            output: {
                "openEuler-logos-openEuler.repo": openEuler:/etc/yum.repos.d/openEuler.repo
            }
        """
        res = {}
        for d_mod in modules:
            print("d_mod is : {}".format(d_mod))
            print("d_mod's type is : {}".format(type(d_mod)))
            feature_list = self.getFeatureInModule(d_mod)
            module_name = d_mod.name()
            xpath = ""
            for d_feature in feature_list:
                xpath = xpath + "/" + module_name + ":" + d_feature
            node = next(self._ctx.find_path(xpath))
            extension = node.get_extension('path')
            path = extension.argument()
            res[module_name] = path

        return res

    def getTypeInModdule(self, modules):
        """
        desc: Return the PATH content of the extension tag in the module
        emaple:
            input: module:openEuler-logos-openEuler.repo
            output: {
                "openEuler-logos-openEuler.repo": ini
            }
        """
        res = {}
        for d_mod in modules:
            if d_mod:
                feature_list = self.getFeatureInModule(d_mod)
                module_name = d_mod.name()
                xpath = ""
                for d_feature in feature_list:
                    xpath = xpath + "/" + module_name + ":" + d_feature
                node = next(self._ctx.find_path(xpath))
                extension = node.get_extension('type')
                d_type = extension.argument()
                res[module_name] = d_type
        return res

    def getSpacerInModdule(self, modules):
        """
        desc: Return the PATH content of the extension tag in the module
        emaple:
            input: module:openEuler-logos-openEuler.repo
            output: {
                "openEuler-logos-openEuler.repo": "="
            }
        """
        res = {}
        for d_mod in modules:
            feature_list = self.getFeatureInModule(d_mod)
            module_name = d_mod.name()
            xpath = ""
            for d_feature in feature_list:
                xpath = xpath + "/" + module_name + ":" + d_feature
            node = next(self._ctx.find_path(xpath))
            extension = node.get_extension('spacer')
            spacer = extension.argument()
            res[module_name] = spacer

        return res

    def getModuleByFilePath(self, filePath):
        """
        desc: return the matching module from the Modules list based on the path.
        input: /etc/yum.repos.d/openEuler.repo
        output: openEuler-logos-openEuler.repo
        """
        res = None
        if len(self._module_list) == 0:
            return None
        for d_module in self._module_list:
            feature_list = self.getFeatureInModule(d_module)
            module_name = d_module.name()
            xpath = ""  
            for d_feature in feature_list:
                xpath = xpath + "/" + module_name + ":" + d_feature
            node = next(self._ctx.find_path(xpath))
            extension = node.get_extension('path')
            ext_path = extension.argument()
            path = ext_path.split(":")[1]
            if path == filePath:
                res = d_module
                break
        return res

    def get_feature_by_real_path(self, domain, real_path):
        """
        desc: return the feature in domain accroding the real_path
        emaxple:
            input: 
                domain:dnf 
                real_path: /etc/yum.repos.d/openEuler.repo
            output:
                feature_path: TARGETDIR/dnf/yum/openEuler.repo
        """
        domain_path = os.path.join(TARGETDIR, domain)
        module = self.getModuleByFilePath(real_path)
        xpath = self.getFeatureInModule(module)
        feature_path = domain_path
        for d_path in xpath:
            feature_path = os.path.join(feature_path, d_path)
        return feature_path

    def check_yang_grammar(self, module_file):
        """
        desc: Use the 'pyang' command to check for syntax problems in the Yang file
        """
        res = False
        gitTools = GitTools()
        cmd = "pyang --ietf {}".format(module_file)
        cmd_code = gitTools.run_shell_return_code(cmd)
        if cmd_code == 0:
            res = True

        return res
