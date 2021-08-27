
# from ordered_dict import OrderedDict as _default_dict
from collections import OrderedDict as _default_dict
import re

class IniConfigParser(object):
    def __init__(self):
        self._dict = _default_dict
        self._sections = self._dict()

    def sections(self):
        """
        desc: return a list of section names.
        """
        return self._sections.keys()

    def add_sections(self, section):
        """
        desc: create a new section in the configuration.
        """
        if section in self._sections:
            return False
        self._sections[section] = self._dict()

    def has_sections(self, section):
        """
        desc: indicate whether the named section is present in the configuration.
        """
        return section in self._sections

    def copy_sections(self, section, new_section_name):
        """
        desc: create a new section accroding pre_section which named new_section_name
        """
        if section in self._sections:
            return False
        new_section = self._sections[section].copy()
        self._sections[new_section_name] = new_section

    def change_sections(self, pre_section, new_section):
        """
        desc: change the sections name from pre_section to new_section
        """
        if pre_section in self._sections:
            return False
        new_section_cont = self._sections[pre_section].copy()
        self._sections[new_section] = new_section_cont
        self.remove_sections(pre_section)

    def remove_sections(self, section):
        """
        desc: remove a file section.
        """
        existed = section in self._sections
        if existed:
            del self._sections[section]
        return existed

    def options(self, section):
        """
        desc: return a list of option name for the section
        """
        res = False
        if section not in self._sections:
            return res
        opts = self._sections[section].copy()
        return opts.keys()

    def get(self, section, option):
        """
        desc: Get value for ``section`` and ``key``.
        """
        res = False
        if section not in self._sections:
            return res
        if option not in self._sections[section]:
            return res
        res = self._sections[section][option]
        return res

    def has_option(self, section, option):
        """
        desc: return a result of the option is in section
        """
        res = False
        existed = section in self._sections
        if not existed:
            return res
        res = option in self._sections[section]
        return res

    def set_option(self, section, option, value=None):
        """
        desc: set an option
        """
        if not section or section not in self._sections:
            return False
        sectdict = self._sections[section]
        sectdict[option] = value

    def remove_option(self, section, option):
        """
        desc: remove an option in section
        """
        res = False
        if not section or section not in self._sections:
            return res
        sectdict = self._sections[section]
        existed = option in sectdict
        if existed:
            del sectdict[option]
        return existed

    # regular expressions for parsing section headers
    SECTCRE = re.compile(
        r'\['                                 # [
        r'(?P<header>[^]]+)'                  # very permissive!
        r'\]'                                 # ]
        )

    # regular expressions for parsing section options
    OPTCRE = re.compile(
        r'(?P<option>[^:=\s][^:=]*)'          # very permissive!
        r'\s*(?P<vi>[:=])\s*'                 # any number of space/tab,
                                              # followed by separator
                                              # (either : or =), followed
                                              # by any # space/tab
        r'(?P<value>.*)$'                     # everything up to eol
        )

    def read(self, content):
        """
        desc: parse a sectioned file.
        """
        lines = content.strip().splitlines()
        cursect = self._dict()
        for line in lines:
            line = line.strip()
            # comment or blank line?
            if line.strip() == '' or line[0] in '#;':
                continue
            mo = self.SECTCRE.match(line)
            if mo:
                sectname = mo.group('header')
                if sectname in self._sections:
                    cursect = self._sections[sectname]
                else:
                    cursect = self._dict()
                    cursect['__name__'] = sectname
                    self._sections[sectname] = cursect
            else:
                mo = self.OPTCRE.match(line)
                if mo:
                    optname, vi, optval = mo.group('option', 'vi', 'value')
                    cursect[optname.strip()] = optval
                else:
                    return False

    def items(self, section):
        """
        desc: return a items of the section.
        """
        sec = self._sections[section]
        if not sec:
            return False

        d_sec = self._dict().copy()
        d_sec.update(sec)
        if "__name__" in d_sec:
            del d_sec["__name__"]
        return dict(d_sec.items())

    def write(self):
        """
        desc: return a content about the representation of the configuration in ini-format
        """
        content = ""
        for section in self._sections:
            content = content + "[{}]\n".format(section)
            for (key, value) in self._sections[section].items():
                if key == "__name__":
                    continue
                if (value is not None) or (self._optcre == self.OPTCRE):
                    key = " = ".join((key, str(value).replace('\n', '\n\t')))
                content = content + key + '\n'
            content = content + '\n'

        return content
