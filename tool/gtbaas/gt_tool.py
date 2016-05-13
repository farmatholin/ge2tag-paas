import json
import logging
import os

from subprocess import Popen, PIPE

from gtbaas.communicator.docker_communicator import DockerCommunicator
from gtbaas.config.app_config import AppConfig
from gtbaas.config.compose_config import ComposeConfig
from gtbaas.user import create_user, load_user

log = logging.getLogger(__name__)


class GtTool(object):
    def __init__(self):
        self.config = AppConfig()
        self.compose_config = ComposeConfig(
            self.config.dc_config_template,
            self.config.image_container
        )
        self.load_ports()
        self.ports_in_use = self.load_ports()
        start, stop = self.config.ports.split('-')
        self.ports_list = set(range(int(start), int(stop) + 1))
        self.dclient = DockerCommunicator()
        self.root_dir = os.path.realpath('.')

    def create(self, user_id, container_id):
        user_container = "{}_{}".format(user_id, container_id)
        user = create_user(user_id, self.config.get_config())
        port = self.get_free_port()
        if port < 0:
            raise FreePortExistError
        log.info("create container {} on port {}".format(container_id, port))
        user.create_container(container_id, port)
        self.ports_in_use[port] = user_container
        self.update_ports()
        return user

    def start(self, user_id, container_id):
        log.info('Starting container')
        os.chdir(os.path.join(self.config.user_root_dir, user_id, container_id))
        rc = manage_script(['docker-compose', 'up', '-d'])
        os.chdir(self.root_dir)
        rc = manage_script(['service', 'nginx', 'reload'])
        log.info('Starting done')

    def stop(self, user_id, container_id):
        log.info('stop container')
        os.chdir(os.path.join(self.config.user_root_dir, user_id, container_id))
        rc = manage_script(['docker-compose', 'stop'])
        os.chdir(self.root_dir)
        log.info('stop done')

    def kill(self, user_id, container_id):
        log.info('kill container')
        os.chdir(os.path.join(self.config.user_root_dir, user_id, container_id))
        rc = manage_script(['docker-compose', 'kill'])
        os.chdir(self.root_dir)
        log.info('kill done')

    def delete(self, user_id, container_id):
        user_container = "{}_{}".format(user_id, container_id)
        log.info("Delete container {}".format(container_id))
        self.kill(user_id, container_id)
        user = load_user(user_id, self.config.get_config())
        user.remove_container(container_id)
        for port in self.ports_in_use.keys():
            if user_container == self.ports_in_use[port]:
                del self.ports_in_use[port]
                self.update_ports()
                return True
        return False

    def load_ports(self):
        try:
            with open(os.path.join(self.config.user_root_dir, 'ports.dat'), 'r+') as ports:
                return json.loads(ports.read())
        except:
            return {}

    def update_ports(self):
        with open(os.path.join(self.config.user_root_dir, 'ports.dat'), 'w+') as ports:
            ports.write(json.dumps(self.ports_in_use))

    def get_free_port(self):
        for port in self.ports_list:
            if str(port) not in self.ports_in_use.keys():
                return port
        return -1

    def init(self):
        log.info("Init tool")
        if not os.path.exists(self.config.user_root_dir):
            log.info("Create user dir")
            os.makedirs(self.config.user_root_dir)
        if not os.path.exists(os.path.join(self.config.user_root_dir, 'ports.dat')):
            log.info("Create files")
            os.mknod(os.path.join(self.config.user_root_dir, 'ports.dat'))
        if not self.dclient.check_image(self.config.image_container):
            log.info("Download image {}".format(self.config.image_container))
            self.dclient.pull_image(self.config.image_container)
        if not self.dclient.check_image(self.config.image_db):
            log.info("Download image {}".format(self.config.image_db))
            self.dclient.pull_image(self.config.image_db)
        log.info("init done")

    def check_images(self):
        if self.dclient.check_image(self.config.image_container) \
                and self.dclient.check_image(self.config.image_db):
            return True
        return False

    def init_check(self):
        if not self.check_images():
            raise InitError
        if not os.path.exists(self.config.user_root_dir) \
                and not os.path.exists(os.path.join(self.config.user_root_dir, 'ports.dat')):
            raise InitError


def manage_script(args):
    child = Popen(args, stdout=PIPE, stderr=PIPE)
    output = child.stdout.read()
    err = child.stderr.read()
    child.communicate()
    rc = child.returncode
    if err == '' and output != '':
        log.info(output)
    log.info(err)
    return rc


class FreePortExistError(Exception):
    pass


class InitError(Exception):
    pass
