import json
import os


class Container(object):
    def __init__(self, container_id, user_path, cpu_chares=50, cpu_quota=25000, mem_limit='150M'):
        self.container_id = container_id
        self.path = os.path.join(user_path, container_id)
        self.logs_path = os.path.join(self.path, "logs")
        self.nginx_log_path = os.path.join(self.path, "nginx_logs")
        self.db_path = os.path.join(self.path, "db")
        self.plugins_path = os.path.join(self.path, "plugins")
        self.status = 'offline'
        self.cpu_shares = int(cpu_chares)
        self.cpu_quota = int(cpu_quota)
        self.mem_limit = mem_limit

    def create(self):
        os.mkdir(self.path)
        os.mkdir(self.logs_path)
        os.mkdir(self.db_path)
        os.mkdir(self.plugins_path)
        os.mkdir(self.nginx_log_path)
        os.mknod(os.path.join(self.nginx_log_path, 'access.log'))
        os.mknod(os.path.join(self.path, 'meta.json'))
        with open(os.path.join(self.path, 'meta.json'), 'w+') as f:
            f.write(json.dumps({
                'cpu_shares': self.cpu_shares,
                'cpu_quota': self.cpu_quota,
                'mem_limit': self.mem_limit
            }))

    def load(self):
        with open(os.path.join(self.path, 'meta.json'), 'r+') as f:
            data = json.loads(f.read())
            self.cpu_shares = data['cpu_shares']
            self.cpu_quota = data['cpu_quota']
            self.mem_limit = data['mem_limit']
