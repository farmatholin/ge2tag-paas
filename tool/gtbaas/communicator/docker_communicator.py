import logging

import sys
from docker import Client

log = logging.getLogger(__name__)


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
