class Container(object):
    def __init__(self, c_id, name, user_id):
        self.name = name
        self.c_id = c_id
        self.user_id = user_id
        self.cpu = 1
        self.mem = 1000
        self.cpu_quota = 100

    @staticmethod
    def get_containers_list(raw_containers):
        if not raw_containers:
            return []
        res = []
        for r_container in raw_containers:
            res.append(Container(
                str(r_container['_id']),
                r_container['name'],
                str(r_container['user_id']),
            ))
        return res
