import os
import json
from swagger_server.utils.yang_module import YangModule
from swagger_server.parses.ini_parse import IniJsonParser

class ObjectParse(object):

    def parse_content_to_json(self, file_path, contents):
        """
        desc: parse the contents to the json accroding the yang file.
        """
        # 加载所有的yang modules:
        yang_modules = YangModule()
        module_list = yang_modules.loadYangModules()
        # module_list = yang_modules.module_list
        print("modulesList is : {}".format(module_list))
        module = yang_modules.getModuleByFilePath(file_path)

        repo = yang_modules.create_ini_object(module)
        yang_modules.add_module_info_in_object(module, repo)
        print("repo is : {}".format(repo))
        print("contents is : {}".format(contents))
        # 将content的内容填充到object内
        object_with_content = yang_modules.add_ini_content_in_object(repo, contents)
        print("object_with_content is : {}".format(object_with_content))
        # 将模型数据转为json数据
        ini_json = IniJsonParser()
        repo_json = ini_json.parse_ini(object_with_content)
        content_string = json.dumps(repo_json, indent = 4, ensure_ascii= False)

        return content_string

    def parse_json_to_object(self, filepath, jsonlist):
        """
        desc: parse the contents to the object accroding the yang file
        """
        # 加载所有的yang modules:
        yang_modules = YangModule()
        module_list = yang_modules.loadYangModules()
        # module_list = yang_modules.module_list
        print("modulesList is : {}".format(module_list))
        module = yang_modules.getModuleByFilePath(filepath)
        print("filepath is : {}".format(filepath))
        print("module is : {}".format(module))
        obj = yang_modules.create_ini_object(module)
        # 将json转为object数据
        ini_json = IniJsonParser()
        repo_json = ini_json.parse_ini_from_dict(obj, jsonlist)
        print("repo_json is : {}".format(repo_json))
        contents = repo_json.parse_dict()

        return contents

