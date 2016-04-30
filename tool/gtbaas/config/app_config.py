import os

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


class AppConfig(object):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('../config/config.ini')
        self.user_root_dir = config['main']['users_root_dir'].strip("\"\'\n\t\r")
        self.dc_config_template = config['main']['config_template'].strip("\"\'\n\t\r")
        self.image_container = config['main']['image_container'].strip("\"\'\n\t\r")
        self.ports = config['main']['ports'].strip("\"\'\n\t\r")

    def get_config(self):
        return vars(self)
