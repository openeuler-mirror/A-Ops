import json
import importlib

from ragdoll.utils.yang_module import YangModule

BASE_PATH = "ragdoll.config_model."
CONFIG_MODEL_NAME = "Config"
PROJECT_NAME = "_config"


class ObjectParse(object):
    def __init__(self):
        self._yang_modules = YangModule()

    def create_conf_model_by_type(self, conf_type):
        """
        desc: Create a structured model corresponding to the configuration type.

        example:
            param: conf_type: ini
            return: IniConfig()
        """
        conf_model = ""
        project_name = conf_type + PROJECT_NAME  # example: ini_config
        project_path = BASE_PATH + project_name  # example: ragdoll.config_model.ini_config
        model_name = conf_type.capitalize() + CONFIG_MODEL_NAME  # example: IniConfig

        try:
            project = importlib.import_module(project_path)
        except ImportError:
            conf_model = ""
        else:
            _conf_model_class = getattr(project, model_name, None)  # example: IniConfig
            if _conf_model_class:
                conf_model = _conf_model_class()  # example: IniConfig()

        return conf_model

    def get_conf_type_by_conf_path(self, conf_path):
        yang_model = self._yang_modules.getModuleByFilePath(conf_path)
        if not yang_model:
            return ""
        _conf_type = self._yang_modules.getTypeInModdule([yang_model])
        conf_type = _conf_type[yang_model.name()]
        return conf_type

    def parse_model_to_json(self, d_model):
        """
        desc: convert object to json.
        """
        conf_json = ""

        conf_dict = d_model.conf
        conf_json = json.dumps(conf_dict, indent=4, ensure_ascii=False)

        return conf_json

    def parse_conf_to_json(self, conf_path, conf_info):
        """
        desc: parse the conf contents to the json accroding the yang file.
        """
        conf_type = self.get_conf_type_by_conf_path(conf_path)
        if not conf_type:
            return ""

        # create conf model
        conf_model = self.create_conf_model_by_type(conf_type)

        # load yang model info
        yang_info = self._yang_modules.getModuleByFilePath(conf_path)
        conf_model.load_yang_model(yang_info)

        # load conf info
        if conf_type == "kv":
            spacer_type = self._yang_modules.getSpacerInModdule([yang_info])
            conf_model.read_conf(conf_info, spacer_type, yang_info)
        else:
            conf_model.read_conf(conf_info)

        # to json
        conf_json = self.parse_model_to_json(conf_model)

        return conf_json

    def parse_json_to_conf(self, conf_path, json_list):
        """
        desc: 将json格式的配置信息解析成原始配置文件格式
        
        """
        conf_type = self.get_conf_type_by_conf_path(conf_path)

        # create conf model
        conf_model = self.create_conf_model_by_type(conf_type)

        # load yang model info
        yang_info = self._yang_modules.getModuleByFilePath(conf_path)
        spacer_info = self._yang_modules.getSpacerInModdule([yang_info])

        # load conf info(json) to model
        conf_model.read_json(json_list)
        if conf_type == "sshd":
            conf_info = conf_model.write_conf(spacer_info)
        elif conf_type == "kv":
            conf_info = conf_model.write_conf(spacer_info, yang_info)
        else:
            # to content
            conf_info = conf_model.write_conf()

        return conf_info
