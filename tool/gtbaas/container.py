import os


class Container(object):
    def __init__(self, container_id, user_path):
        self.container_id = container_id
        self.path = os.path.join(user_path, container_id)
        self.logs_path = os.path.join(self.path, "logs")
        self.db_path = os.path.join(self.path, "db")
        self.plugins_path = os.path.join(self.path, "plugins")
        self.status = 'offline'

    def create(self):
        os.mkdir(self.path)
        os.mkdir(self.logs_path)
        os.mkdir(self.db_path)
        os.mkdir(self.plugins_path)
