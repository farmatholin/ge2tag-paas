import os

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


class AppConfig(object):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('../config/config.ini')
        self.user_root_dir = os.path.abspath(config['main']['users_root_dir']).strip("\"\'\n\t\r")
        self.dc_config_template = config['main']['config_template']

    def get_config(self):
        return vars(self)
