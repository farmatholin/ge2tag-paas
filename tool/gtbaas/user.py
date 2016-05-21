import os
import shutil

from gtbaas.config.compose_config import ComposeConfig
from gtbaas.config.nginx_config import NginxConfig
from gtbaas.container import Container


class User(object):
    def __init__(self, user_id, path, compose_config, nginx_config):
        self.user_id = user_id
        self.compose_config = compose_config
        self.nginx_config = nginx_config
        self.path = path
        self.containers = {}

    def create(self):
        os.mkdir(self.path)

    def load(self):
        self.load_containers()

    def create_container(self, container_id, port, cpu_chares, cpu_quota, mem_limit):
        if container_id in self.containers.keys():
            return self.containers[container_id]

        container = Container(container_id, self.path, cpu_chares, cpu_quota, mem_limit)
        container.create()
        self.create_config(container, port)
        self.create_nginx_config(container, port)
        self.containers[container_id] = container
        return container

    def load_containers(self):
        dirs = os.listdir(self.path)
        for container in dirs:
            con = Container(container, self.path)
            con.load()
            self.containers[container] = con

    def create_config(self, container, port):
        self.compose_config.create_config(self,port, container)

    def create_nginx_config(self, container, port):
        self.nginx_config.create_config(self, container, port)

    def remove_container(self, container_id):
        shutil.rmtree(os.path.join(self.path, container_id))
        self.nginx_config.remove(self, container_id)
        del self.containers[container_id]


def load_user(user_id, config):
    compose_config = ComposeConfig(config['dc_config_template'], config['image_container'])
    nginx_config = NginxConfig(config['nginx_template'], config['site'])
    user_path = os.path.join(config['user_root_dir'], user_id)
    user = User(user_id, user_path, compose_config, nginx_config)
    user.load()
    return user


def create_user(user_id, config):
    user_path = os.path.join(config['user_root_dir'], user_id)
    if os.path.exists(user_path):
        return load_user(user_id, config)
    compose_config = ComposeConfig(config['dc_config_template'], config['image_container'])
    nginx_config = NginxConfig(config['nginx_template'], config['site'])
    user = User(user_id, user_path, compose_config, nginx_config)
    user.create()
    return user
