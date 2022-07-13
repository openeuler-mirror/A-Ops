import sys
import time
import signal
import subprocess
import os
import io
import getopt
import requests
import libconf

DOCKER = "/docker/"
DOCKER_LEN = 8
g_meta = None
g_metric = None


def convert_meta():
    '''
    Convert the meta file like the following format:
    g_meta[container_blkio] = 
    {
        'id': 0,
        'device': 0,
        'major': 0,
        'minor': 0,
        'operation': 0,
        'device_usage_total': 0
    }
    '''
    global g_meta
    with io.open("/opt/gala-gopher/meta/cadvisor_probe.meta", encoding='utf-8') as f:
        meta = libconf.load(f)
        g_meta = dict()
        for measure in meta.measurements:
            g_meta[measure.table_name] = dict()
            for field in measure.fields:
                g_meta[measure.table_name][field.name] = 0


def find_2nd_index(stri, key):
    first = stri.index(key) + 1
    after_str = stri[first:]
    try:
        index = after_str.index(key)
    except Exception as e:
        index = len(after_str)
    return first + index


def parse_metrics(raw_metrics):
    global g_metric
    g_metric = dict()
    for line in raw_metrics.splitlines():
        if line.startswith("container_"):
            delimiter = find_2nd_index(line, "_")
            table_name = line[:delimiter]
            if table_name not in g_meta:
                continue
            if table_name not in g_metric:
                g_metric[table_name] = dict()

            metric_str = libconf.loads(line[(line.index("{") + 1):line.index("} ")])
            # TODO: will filter out system processes by whitelist
            if not metric_str.id.startswith(DOCKER):
                continue

            hashed_metric_str = frozenset(metric_str.items())
            if hashed_metric_str not in g_metric[table_name]:
                g_metric[table_name][hashed_metric_str] = metric_str
                g_metric[table_name][hashed_metric_str]['container_id'] = metric_str.id[DOCKER_LEN:]

            metric_name = line[line.index("_") + 1:line.index("{")]
            g_metric[table_name][hashed_metric_str][metric_name] = \
                line[(line.index(" ") + 1):find_2nd_index(line, " ")]


def print_metrics():
    global g_metric
    global g_meta
    for table, records in g_metric.items():
        if table not in g_meta:
            continue
        for record in records.values():
            s = "|" + table + "|"
            if table in g_meta:
                for field in g_meta[table]:
                    if field not in record:
                        value = ""
                    else:
                        value = record[field]
                    s = s + value + "|"
                print(s)


def clean_metrics():
    global g_metric
    g_metric = None


class CadvisorProbe(object):
    def __init__(self, port_c):
        self.port = port_c
        self._pid = None
        self._redis_info = None

    def get_cadvisor_port(self):
        p = subprocess.Popen("/usr/bin/netstat -natp | /usr/bin/grep cadvisor | /usr/bin/grep LISTEN | \
                            /usr/bin/awk  -F \":::\" '{print $2}'", stdout=subprocess.PIPE, shell=True)
        (rawout, serr) = p.communicate(timeout=5)
        if len(rawout) != 0:
            self.port = rawout.rstrip().decode()
            return True
        return False

    def start_cadvisor(self):
        p = subprocess.Popen("/usr/bin/ps -ef | /usr/bin/grep /usr/bin/cadvisor | /usr/bin/grep -v grep | \
                            /usr/bin/awk '{print $2}'", stdout=subprocess.PIPE, shell=True)
        (rawout, serr) = p.communicate(timeout=5)
        if len(rawout) != 0:
            self._pid = rawout.rstrip().decode()
            if self.get_cadvisor_port():
                print("[cadvisor_probe]cAdvisor has already been running at port %s." % self.port)
                return
            else:
                raise Exception('[cadvisor_probe]cAdvisor running but get info failed')
        ps = subprocess.Popen(["/usr/bin/cadvisor", "-port", str(self.port)], stdout=subprocess.PIPE, shell=False)
        self._pid = ps.pid
        print("[cadvisor_probe]cAdvisor started at port %s." % self.port)

    def stop_cadvisor(self):
        print("[cadvisor_probe]stop cAdvisor before exit.")
        subprocess.Popen(["/usr/bin/kill", "-9", str(self._pid)], stdout=subprocess.PIPE, shell=False)
        sys.exit(0)

    def signal_handler(self, signum, frame):
        self.stop_cadvisor()

    def get_metrics(self):
        url = "http://localhost:%s/metrics" % (self.port)
        r = requests.get(url)
        r.raise_for_status()

        parse_metrics(r.text)
        print_metrics()
        clean_metrics()


def get_param():
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "p:d:")

    port = 0
    period = 5
    for opt, arg in opts:
        if opt in ["-p"]:
            port = int(arg)
        elif opt in ["-d"]:
            period = int(arg)
    if port == 0:
        raise Exception('[cadvisor_probe]no port param specified')
    return port, period


if __name__ == "__main__":
    conf_port, conf_period = get_param()
    probe = CadvisorProbe(conf_port)
    probe.start_cadvisor()
    signal.signal(signal.SIGINT, probe.signal_handler)
    convert_meta()

    while True:
        time.sleep(conf_period)
        try:
            probe.get_metrics()
        except Exception as e:
            print("[cadvisor_probe]get metrics failed. Err: %s" % repr(e))
