CONTAINER__STATUS_ONLINE = 'online'
CONTAINER__STATUS_OFFLINE = 'offline'


class Container(object):
    def __init__(self, c_id, name, user_id, host, status=CONTAINER__STATUS_OFFLINE):
        self.name = name
        self.c_id = c_id
        self.user_id = user_id
        self.ram = "150M"
        self.cpu = 25
        self.status = status
        self.host = host

    @staticmethod
    def get_containers_list(raw_containers):
        if not raw_containers:
            return []
        res = []
        for r_container in raw_containers:
            con = Container(
                str(r_container['_id']),
                r_container['name'],
                str(r_container['user_id']),
                str(r_container['host']),
                str(r_container['status']),
            )
            con.mem = str(r_container.get('ram', '150M'))
            con.cpu = int(r_container.get('cpu', '25'))
            res.append(con)
        return res
