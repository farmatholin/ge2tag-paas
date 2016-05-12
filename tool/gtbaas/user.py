import os

from gtbaas.config.compose_config import ComposeConfig
from gtbaas.container import Container


class User(object):
    def __init__(self, user_id, path, compose_config):
        self.user_id = user_id
        self.compose_config = compose_config
        self.path = path
        self.containers = {}

    def create(self):
        os.mkdir(self.path)

    def load(self):
        self.load_containers()

    def create_container(self, container_id, port):
        if container_id in self.containers.keys():
            return self.containers[container_id]

        container = Container(container_id, self.path)
        container.create()
        self.create_config(container, port)
        self.containers[container_id] = container
        return container

    def load_containers(self):
        dirs = os.listdir(self.path)
        for container in dirs:
            self.containers[container] = Container(container, self.path)

    def create_config(self, container, port):
        self.compose_config.create_config(port, container)

    def remove_container(self, container_uid):
        pass


def load_user(user_id, config):
    compose_config = ComposeConfig(config['dc_config_template'], config['image_container'])
    user_path = os.path.join(config['user_root_dir'], user_id)
    user = User(user_id, user_path, compose_config)
    user.load()
    return user


def create_user(user_id, config):
    user_path = os.path.join(config['user_root_dir'], user_id)
    if os.path.exists(user_path):
        return load_user(user_id, config)
    compose_config = ComposeConfig(config['dc_config_template'], config['image_container'])
    user = User(user_id, user_path, compose_config)
    user.create()
    return user
