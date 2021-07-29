
from swagger_server.analy.ini_config_parser import IniConfigParser  # noqa: E501

class OpenEulerRepo(object):

    def __init__(self):
        self.data = IniConfigParser()

    def parse_content(self, content):
        self.data.read(content)

    def parse_dict(self):
        return self.data.write()

    def sections(self):
        return self.data.sections()

    def get(self, section, key):
        return self.data.get(section, key)

    def items(self, section):
        return self.data.items(section)

    def add_sections(self, section):
        return self.data.add_sections(section)

    def has_sections(self, section):
        return self.data.has_sections(section)

    def copy_sections(self, section, new_section):
        return self.data.copy_sections(section, new_section)

    def change_sections(self, pre_section, new_section):
        return self.data.change_sections(pre_section, new_section)

    def remove_sections(self, section):
        return self.data.remove_sections(section)

    def options(self, section):
        return self.data.options(section)

    def has_option(self, section, key):
        return self.data.has_option(section, key)

    def set_option(self, section, option, value=None):
        return self.data.set_option(section, option, value)

    def remove_option(self, section, option):
        return self.data.remove_option(section, option)