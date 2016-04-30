from gtbaas.config.app_config import AppConfig
from gtbaas.config.compose_config import ComposeConfig
from gtbaas.user import create_user


class GtTool(object):
    def __init__(self):
        self.config = AppConfig()
        self.compose_config = ComposeConfig(self.config.dc_config_template)

    def create(self, user_id):
        return create_user(user_id, self.config.get_config())

    def start(self, user):
        pass
