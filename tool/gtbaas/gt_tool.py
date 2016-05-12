import json
import os

from gtbaas.config.app_config import AppConfig
from gtbaas.config.compose_config import ComposeConfig
from gtbaas.user import create_user


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

    def create(self, user_id, container_id):
        user = create_user(user_id, self.config.get_config())
        port = self.get_free_port()
        if port > 0:
            user.create_container(container_id, port)
            self.ports_in_use[port] = container_id
            self.update_ports()
            return user
        else:
            raise FreePortExistError

    def start(self, user, container_id):
        pass

    def stop(self, user, container_id):
        pass

    def delete(self, user, container_id):
        pass

    def load_ports(self):
        with open(os.path.join(self.config.user_root_dir, 'ports.dat'), 'r+') as ports:
            try:
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


class FreePortExistError(Exception):
    pass
