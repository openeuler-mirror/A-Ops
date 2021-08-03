import libyang
import os
import sys
import importlib
import operator
from ragdoll.analy.openEuler_repo import OpenEulerRepo

PROJECTNAME = "gala-ragdoll-1.0.0"
TARGETDIR = "/home/confTrace"

class YangModule(object):
    def __init__(self):
        self._cwd_dir = os.getcwd()
        self._target_dir = "yang_modules"
        self._ctx = libyang.Context()
        self._module_list = []
        self._yang_dir = ""
        self.loadYangModules()

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
    def module_list(self):
        return self._module_list

    @module_list.setter
    def module_list(self, module_list):
        return self._module_list

    def loadYangModules(self) -> []:
        """
        desc: load the yang modules in the path of ../../yang_modules
        """
        self._ctx = libyang.Context()
        # cwdDir = os.getcwd() 
        print("this.pwd_dir is : {}".format(self._cwd_dir))
        paths = self._cwd_dir.split("/")
        print("paths is : {}".format(paths))
        index = paths.index(PROJECTNAME)
        print("index is : {}".format(index))
        yang_path = ""
        for d_index in range(1, index + 1):
            yang_path = yang_path + "/" + paths[d_index]
        yangDir = os.path.join(yang_path, self._target_dir)
        print("yangDir is : {}".format(yangDir))
        self._yang_dir = yangDir
        for root, dirs, files in os.walk(yangDir):
            for d_file in files:
                # print("this file is : {}".format(d_file))
                modulePath = os.path.join(yangDir, d_file)
                print("modulePath is : {}".format(modulePath))
                fo = open(modulePath, 'r+')
                module = self._ctx.parse_module_file(fo)
                self._module_list.append(module)
                fo.close()
        print("module_list is : {}".format(self._module_list))
        return self._module_list

    def getXpathInModule(self, modules) -> []:
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
        方案：由于第一层node是2个空格，后面每增加一层node，就增加三个空格，所以采用空格来进行判断层级数
        采用 '+--rw' 前面的空格数减2除3取商来判断层级 
        """
        xpath=[]
        level = []
        init_index = 0
        tree_node = modules.print_mem()
        tree_lines = tree_node.splitlines()
        len_tree = len(tree_lines)
        path = ""
        # 是否可以采用 (node - 2）/ 3的商作为层次数值
        for count in range(0, len_tree):
            line = tree_lines[count]
            if not len(line) or line.startswith('module'):
                continue
            tree_split = line.split(' ')
            index = tree_split.index('+--rw')
            index_next = tree_split[index + 1]
            # print("index is :{}".format(index))
            # print("current is : {}".format(index_next))
            # print("init_index is : {}".format(init_index))
            # print("level is : {}".format(level))
            if not index_next[len(index_next) - 1].isalpha():
                index_next = index_next[0 : len(index_next) - 1]
            if index == init_index:
                prePath = ""
                for count_temp in range(0, len(level) - 1):
                    prePath += level[count_temp] + '/'
                # print("this prePath is : {}".format(prePath))
                path = prePath + index_next
                preLevel = level[len(level) - 1]
                level = level[0 : len(level) - 1]
                # print("xpath is : {}".format(xpath))
                if len(xpath) > 0:
                    last = xpath[len(xpath) - 1]
                    if last[len(last) - 1] is '/':
                        xpath[len(xpath) - 1] = last[0 : len(last) - 1]
                    level.append(index_next)
                    # print("this path is : {}".format(path))
                    xpath.append(path)
                    continue
                else:
                    level.append(index_next)
                    firstPath = prePath + preLevel
                    # print("firstPath is : {}".format(firstPath))
                    xpath.append(firstPath)
            elif index > init_index:
                path += index_next + '/'
                init_index = index
                level.append(index_next)
                continue
            else:
                level_num = (index - 2 ) / 3
                level = level[0: level_num]
                init_index = index
                for d_level in level:
                    path += level[d_level] + '/'
                level.append(index_next)
            xpath.append(path)
            # print("path is : {}".format(path))
            # print("xpath is : {}".format(xpath))

        # print("xpath is : {}".format(xpath))
        return xpath

    def getFeatureInModule(self, modules) -> []:
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
        print("modules is : {}".format(modules))
        print("type of modules is : {}".format(type(modules)))
        tree_node = modules.print_mem()
        tree_lines = tree_node.splitlines()
        # module 的tree中只需要获取第二行和第三行
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
        print("self._module_list is : {}".format(self._module_list))
        print("len of len(self._module_list) is : {}".format(len(self._module_list)))
        if len(self._module_list) > 0:
            for d_module in self._module_list:
                feature_list = self.getFeatureInModule(d_module)
                res = operator.eq(feature_paths.sort(), feature_list.sort())
                if res == 1:
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
        res = ""
        if len(self._module_list) == 0:
            return null
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

    def create_ini_object(self, module):
        """
        desc: create an object according to the model and add the model to the object
        example:
            input: module = 'openEuler-logos-openEuler.repo'
            output: OpenEulerRepo()
        """
        module_name = module.name().split('-')[-1]

        object_name = ""
        if '.' in module_name:
            spl_name = module_name.split('.')
            for d_name in spl_name:
                object_name = object_name + d_name[:1].upper() + d_name[1:]
        else:
            object_name = module_name[:1].upper() + module_name[1:]

        project_name = module_name.replace('.', '_')
        all_path = "ragdoll.analy." + project_name
        project = importlib.import_module(all_path)
        module_obj = getattr(project, object_name)
        res = module_obj()
        return res

    def add_module_info_in_object(self, module, module_obj):
        """
        desc: add module info in object
        """
        print("module is : {}".format(module))
        print("module_obj is : {}".format(module_obj))
        # 获取module的xpath
        xpath = self.getXpathInModule(module)
        for d_xpath in xpath:
            real_path = d_xpath.split('/')
            section = real_path[2]
            option = real_path[3]
            print("section is : {}".format(section))
            print("option is : {}".format(option))
            if module_obj.has_sections(section):
                module_obj.set_option(section, option)
            else:
                module_obj.add_sections(section)
                module_obj.set_option(section, option)

    def add_ini_content_in_object(self, module_obj, content):
        """
        desc: Add content to the object according to the restrictions of the module
        """
        repo = OpenEulerRepo()
        repo.parse_content(content)
        if not repo.data.sections():
            return False

        res = OpenEulerRepo()

        sections_module = module_obj.sections()
        sections_repo = repo.sections()

        for repo_section in sections_repo:
            repo_options = repo.options(repo_section)
            print("repo repo_section is : {}".format(repo_section))
            # 将repo中的section 与module中的section进行模糊匹配
            print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            print("repo_options is : {}".format(repo_options))
            m_section = self.get_mactch_section(repo_options, module_obj)
            for d_opt in repo_options:
                if d_opt is "__name__":
                    continue
                value = repo.get(repo_section, d_opt)
                if m_section is not None:
                    if res.has_sections(repo_section):
                        res.set_option(repo_section, d_opt, value)
                    else:
                        res.add_sections(repo_section)
                        res.set_option(repo_section, d_opt, value)
        return res

    def get_mactch_section(self, option_list, obj):
        res = None
        for m_section in obj.sections():
            m_options = list(obj.options(m_section))
            count = 0
            for d_option in list(option_list):
                if d_option in m_options:
                    count = count + 1
            if len(option_list) == 1 and count == 1:
                res = m_section
                break
            else:
                if count > 2:
                    res = m_section
                    break
        print("res is : {}".format(res))
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