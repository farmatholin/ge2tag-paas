import os


class User(object):
    def __init__(self, user_id, path):
        self.user_id = user_id
        self.path = path
        self.logs_path = os.path.join(self.path, "logs")
        self.db_path = os.path.join(self.path, "db")
        self.plugins_path = os.path.join(self.path, "plugins")

    def create(self):
        os.mkdir(self.path)
        os.mkdir(self.logs_path)
        os.mkdir(self.db_path)
        os.mkdir(self.plugins_path)


def load_user(user_id, config):
    user_path = os.path.join(config['user_root_dir'], user_id)
    return User(user_id, user_path)


def create_user(user_id, config):
    user_path = os.path.join(config['user_root_dir'], user_id)

    if os.path.exists(user_path):
        return load_user(user_id, config)
    user = User(user_id, user_path)
    user.create()
    return user
