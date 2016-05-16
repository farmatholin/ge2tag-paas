from werkzeug.security import check_password_hash


class User(object):
    def __init__(self, user_id, username):
        self.username = username
        self.user_id = user_id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user_id

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)
