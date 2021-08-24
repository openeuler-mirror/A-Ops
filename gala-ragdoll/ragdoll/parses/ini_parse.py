
from ragdoll.analy.ini_config_parser import IniConfigParser

import json

class IniJsonParse(object):
    """
    Class: 'IniJsonParse' parses the object which the type of IniConfigParser
    """
    def __init__(self):
        self.data = ""

    def parse_ini(self, obj):
        """
        desc: return an json from obj
        """
        self.data = self.parse_dict_from_ini(obj)
        return self.data

    def parse_content(self, obj, dic):
        """
        desc: return a content from object
        """
        self.data = self.parse_ini_from_dict(obj, dic)
        return self.data

    def parse_dict_from_ini(self, obj):
        """
        desc: return an json listfrom the obj object
        """
        dic = {}
        sections = obj.sections()
        for d_sec in sections:
            d_dic = {}
            options = obj.options(d_sec)
            for d_opt in options:
                value = obj.get(d_sec, d_opt)
                d_dic[d_opt] = value
            dic[d_sec] = d_dic

        return dic

    def parse_ini_from_dict(self, obj, dic):
        """
        desc: return an ini object from the json
        """
        json_code = json.loads(dic)
        for key, value in json_code.items():
            obj.add_sections(key)
            for key2, value2 in value.items():
                obj.set_option(key, key2, value2)

        print("obj is : {}".format(obj))

        return obj
