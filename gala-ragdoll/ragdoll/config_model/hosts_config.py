import re
import json

NOT_SYNCHRONIZE = "NOT SYNCHRONIZE"
SYNCHRONIZED = "SYNCHRONIZED"

ipv4 = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')

ipv6 = re.compile('^((([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4})|'
                  '(([0-9A-Fa-f]{1,4}:){1,7}:)|'
                  '(([0-9A-Fa-f]{1,4}:){6}:[0-9A-Fa-f]{1,4})|'
                  '(([0-9A-Fa-f]{1,4}:){5}(:[0-9A-Fa-f]{1,4}){1,2})|'
                  '(([0-9A-Fa-f]{1,4}:){4}(:[0-9A-Fa-f]{1,4}){1,3})|'
                  '(([0-9A-Fa-f]{1,4}:){3}(:[0-9A-Fa-f]{1,4}){1,4})|'
                  '(([0-9A-Fa-f]{1,4}:){2}(:[0-9A-Fa-f]{1,4}){1,5})|'
                  '([0-9A-Fa-f]{1,4}:(:[0-9A-Fa-f]{1,4}){1,6})|'
                  '(:(:[0-9A-Fa-f]{1,4}){1,7})|'
                  '(([0-9A-Fa-f]{1,4}:){6}(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])'
                  '(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3})|'
                  '(([0-9A-Fa-f]{1,4}:){5}:(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])'
                  '(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3})|'
                  '(([0-9A-Fa-f]{1,4}:){4}(:[0-9A-Fa-f]{1,4})'
                  '{0,1}:(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3})|'
                  '(([0-9A-Fa-f]{1,4}:){3}(:[0-9A-Fa-f]{1,4}){0,2}:(\\d|[1-9]\\d|1\\d{2}|'
                  '2[0-4]\\d|25[0-5])(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3})|'
                  '(([0-9A-Fa-f]{1,4}:){2}(:[0-9A-Fa-f]{1,4}){0,3}:(\\d|[1-9]\\d|1\\d{2}|'
                  '2[0-4]\\d|25[0-5])(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3})|'
                  '([0-9A-Fa-f]{1,4}:(:[0-9A-Fa-f]{1,4}){0,4}:(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])'
                  '(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3})|'
                  '(:(:[0-9A-Fa-f]{1,4}){0,5}:(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])'
                  '(\\.(\\d|[1-9]\\d|1\\d{2}|2[0-4]\\d|25[0-5])){3}))$')


class HostsConfig:

    def __int__(self):
        pass

    @staticmethod
    def _parse_network_conf_to_dict(conf_info):

        res = dict()
        error_conf = False

        conf_info_list = conf_info.split("\n")
        for line in conf_info_list:
            if line.strip() == '' or line.strip()[0] in '#':
                continue
            ip_domain = re.split("\s+", line)
            if len(ip_domain) == 1:
                error_conf = True
                break
            ip = ip_domain[0]
            if ipv4.match(ip) or ipv6.match(ip):
                list_value = ip_domain[1:]
                str_value = " ".join(list_value)
                res[ip] = str_value
            else:
                error_conf = True
                break

        return error_conf, res

    def parse_res_to_json(self, conf_info):
        conf_json = ""

        error_conf, dict_res = self._parse_network_conf_to_dict(conf_info.strip())
        if not error_conf:
            conf_json = json.dumps(dict_res, indent=4, ensure_ascii=False)

        return conf_json

    @staticmethod
    def conf_compare(dst_conf, src_conf):
        """
        desc: 比较dst_conf和src_conf是否相同，dst_conf和src_conf均为序列化后的配置信息。
        return：dst_conf和src_conf相同返回SYNCHRONIZED
                        dst_conf和src_conf不同返回NOT_SYNCHRONIZE
        """
        res = SYNCHRONIZED
        dst_conf_dict = json.loads(dst_conf)
        src_conf_dict = json.loads(src_conf)

        dst_conf_keys = dst_conf_dict.keys()
        src_conf_keys = src_conf_dict.keys()

        for src_key in src_conf_keys:
            if src_key not in dst_conf_keys:
                res = NOT_SYNCHRONIZE
                break
            if str(dst_conf_dict[src_key]) != str(src_conf_dict[src_key]):
                res = NOT_SYNCHRONIZE
                break
        return res

    @staticmethod
    def read_conf(conf_json):
        """
        desc: 将json格式的配置文件内容结构化。
        """
        conf_dict = json.loads(conf_json)
        return conf_dict

    @staticmethod
    def write_conf(conf_dict):
        content = ""
        conf_dict_keys = conf_dict.keys()
        for key in conf_dict_keys:
            if conf_dict[key] is not None:
                conf_item = " ".join((key, str(conf_dict[key]))).replace('\n', '\n\t')
                content = content + conf_item + "\n"
        return content
