import redis
import subprocess

REDIS_HOST = "127.0.0.1"
REDIS_PORT = "6379"


class RedisProbe(object):

    def __init__(self, host, port):
        self._host = host
        self._port = port

    def get_data(self):
        self._get_redis_info()
        self._get_redis_latency()

    def _get_redis_info(self):
        redis_conn = redis.Redis(host=self._host, port=self._port)
        info = redis_conn.info()
        print(info)
        redis_conn.close()

    def _get_redis_latency(self):
        command = "redis-cli -h %s -p %s --intrinsic-latency 1" % (self._host, self._port)
        ex = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        out, err = ex.communicate()
        print(out.decode())


if __name__ == "__main__":
    probe = RedisProbe(REDIS_HOST, REDIS_PORT)
    probe.get_data()
