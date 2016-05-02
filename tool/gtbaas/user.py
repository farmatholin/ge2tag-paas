import os

from gtbaas.config.compose_config import ComposeConfig


class User(object):
    def __init__(self, user_id, path, compose_config):
        self.user_id = user_id
        self.compose_config = compose_config
        self.path = path
        self.logs_path = os.path.join(self.path, "logs")
        self.db_path = os.path.join(self.path, "db")
        self.plugins_path = os.path.join(self.path, "plugins")

    def create(self):
        os.mkdir(self.path)
        os.mkdir(self.logs_path)
        os.mkdir(self.db_path)
        os.mkdir(self.plugins_path)

    def create_config(self, port):
        self.compose_config.create_config(port, self.user_id, {
            'user_dir': self.path,
            'logs_path': self.logs_path,
            'db_path': self.db_path,
            'plugins_path': self.plugins_path
        })


def load_user(user_id, config):
    compose_config = ComposeConfig(config['dc_config_template'], config['image_container'])
    user_path = os.path.join(config['user_root_dir'], user_id)
    return User(user_id, user_path, compose_config)


def create_user(user_id, config):
    user_path = os.path.join(config['user_root_dir'], user_id)
    if os.path.exists(user_path):
        return load_user(user_id, config)
    compose_config = ComposeConfig(config['dc_config_template'], config['image_container'])
    user = User(user_id, user_path, compose_config)
    user.create()
    return user
