import json
import logging

import sys
from docker import Client

log = logging.getLogger(__name__)


def get_cpu_usage(stats_json):
    cpu_percent = float()
    cpu_delta = stats_json['cpu_stats']['cpu_usage']['total_usage'] - stats_json['precpu_stats']['cpu_usage'][
        'total_usage']
    sys_delta = stats_json['cpu_stats']['system_cpu_usage'] - stats_json['precpu_stats']['system_cpu_usage']

    if sys_delta > 0.0 and cpu_delta > 0.0:
        part = float(cpu_delta) / float(sys_delta)
        cpu_percent = part * len(stats_json['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
    return round(cpu_percent, 2)


def get_mem_usage(stats_json):
    return (int(stats_json['memory_stats']['usage']) / 1024) / 1024


class DockerCommunicator(object):
    def __init__(self):
        self.cli = Client()

    def pull_image(self, name, tag='latest'):
        log.info("Downloading {}:{}".format(name, tag))
        for line in self.cli.pull(name, tag, stream=True):
            sys.stdout.write('.')
            sys.stdout.flush()
        sys.stdout.write('\n')
        log.info("Downloading {}:{} done".format(name, tag))

    def check_image(self, name):
        if not self.cli.images(name):
            return False
        return True

    def stats(self, name):
        res = self.cli.stats(name, stream=False)
        # stats = res #json.loads(res)

        return {
            'cpu_usage': get_cpu_usage(res),
            'mem_usage': get_mem_usage(res)
        }
