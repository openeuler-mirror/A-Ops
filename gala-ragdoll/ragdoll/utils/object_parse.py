import os
import json
import importlib
from ragdoll.utils.yang_module import YangModule
from ragdoll.parses.ini_parse import IniJsonParse
from ragdoll.analy.ini_config_parser import IniConfigParser

ANALYPATH = "ragdoll.analy."
CONFIGPARSERNAME = "ConfigParser"
OBJECTFILENAME = "_config_parser"
PARSE = "parse"
PARSEPATH = "ragdoll.parses."


class ObjectParse(object):

    def parse_content_to_json(self, file_path, contents):
        """
        desc: parse the contents to the json accroding the yang file.
        """
        # load all yang modules:
        yang_modules = YangModule()
        module_list = yang_modules.module_list
        module = yang_modules.getModuleByFilePath(file_path)
        d_type = yang_modules.getTypeInModdule([module])
        conf_type = d_type[module.name()]
        repo = self.creat e_object_by_type(conf_type)
        # Fill an object with content
        object_with_content = ""
        if conf_type == "ini":
            self.add_ini_module_info_in_object(module, repo)
            object_with_content = self.parse_ini_content_to_object(repo, contents)
        # Convert model data to JSON data
        ini_json = self.create_parse_by_type(conf_type)
        content_string = self.parse_object_to_json(object_with_content, conf_type)
        return content_string

    def parse_json_to_content(self, filepath, jsonlist):
        """
        desc: parse the contents to the object accroding the yang file
        """
        # load all yang modules:
        yang_modules = YangModule()
        module_list = yang_modules.module_list
        module = yang_modules.getModuleByFilePath(filepath)
        d_type = yang_modules.getTypeInModdule([module])
        conf_type = d_type[module.name()]
        obj = self.create_object_by_type(conf_type)
        # Convert JSON data into model data
        d_object = self.parse_json_to_object(obj, jsonlist, conf_type)
        contents = ""
        if d_object and conf_type == "ini":
            contents = self.parse_object_to_ini_content(d_object)

        return contents

    def create_object_by_type(self, d_type):
        """
        desc: create a object accroding the type.
        """
        project_name = d_type + OBJECTFILENAME
        object_name = d_type.capitalize() + CONFIGPARSERNAME
        all_path = ANALYPATH + project_name
        project = importlib.import_module(all_path)
        module_obj = getattr(project, object_name)
        res = module_obj()
        return res

    def add_ini_module_info_in_object(self, module, module_obj):
        """
        desc: add module info in object
        """
        # get all xpath in yang module
        yang_module = YangModule()
        xpath = yang_module.getXpathInModule(module)
        for d_xpath in xpath:
            real_path = d_xpath.split('/')
            section = real_path[2]
            option = real_path[3]
            if module_obj.has_sections(section):
                module_obj.set_option(section, option)
            else:
                module_obj.add_sections(section)
                module_obj.set_option(section, option)

    def parse_ini_content_to_object(self, module_obj, contents):
        """
        desc: parse the contents of type INI to the object accroding the yang file.
        """
        content_obj = self.create_object_by_type("ini")
        content_obj.read(contents)
        if not content_obj.sections():
            return False

        res = self.create_object_by_type("ini")
        sections_mod = module_obj.sections()
        sections_cont = content_obj.sections()

        for c_section in sections_cont:
            cont_options = content_obj.options(c_section)
            m_section = self.get_mactch_section(cont_options, module_obj)
            for d_opt in cont_options:
                if d_opt is "__name__":
                    continue
                value = content_obj.get(c_section, d_opt)
                if m_section is not None:
                    if res.has_sections(c_section):
                        res.set_option(c_section, d_opt, value)
                    else:
                        res.add_sections(c_section)
                        res.set_option(c_section, d_opt, value)
        return res

    def get_mactch_section(self, option_list, obj):
        """
        desc: Blur matches two objects by option
        """
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
        return res

    def create_parse_by_type(self, d_type):
        """
        desc: create the parse object the type of d_type
        """
        project_name = d_type + "_" + PARSE
        object_name = d_type.capitalize() + "Json" + PARSE.capitalize()
        all_path = PARSEPATH + project_name
        project = importlib.import_module(all_path)
        d_object = getattr(project, object_name)
        res = d_object()
        return res

    def parse_object_to_json(self, d_object, d_type):
        """
        desc: convert object to json.
        """
        content_string = ""
        parse_obj = self.create_parse_by_type(d_type)
        if d_type == "ini":
            repo_json = parse_obj.parse_ini(d_object)
            content_string = json.dumps(repo_json, indent = 4, ensure_ascii= False)
        return content_string

    def parse_object_to_ini_content(self, obj):
        """
        desc: parse the object to the content of type INI accroding the yang file.
        """
        content = obj.write()
        content_string = json.dumps(content, indent = 4, ensure_ascii= False)
        return content

    def parse_json_to_object(self, parse_object, d_json, d_type):
        """
        desc: convert json to object.
        """
        d_object = None
        parse_obj = self.create_parse_by_type(d_type)
        if d_type == "ini":
            d_object = parse_obj.parse_content(parse_object, d_json)
        return d_object
