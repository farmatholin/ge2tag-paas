import time
import threading
import requests

from app import app


def usage_stats():
    threads = []
    users = app.config['USERS_COLLECTION'].find({})
    for user in users:
        containers = app.config['CONTAINERS_COLLECTION'].find({"user_id": user['_id']})
        for container in containers:
            if container['status'] == 'online':
                try:
                    t = threading.Thread(target=container_gather, args=(user, container))
                    t.start()
                    threads.append(t)
                except:
                    print "thread error"
            else:
                print 'error'
    for t in threads:
        t.join()


def container_gather(user, container):
    res = requests.post(
        'http://{}:{}/stats'.format(
            app.config['TOOL_SERVER'], app.config['TOOL_PORT'])
        , json={
            "container": container['name'],
            "user": user['username'],
        }
    )
    if res.ok and int(res.json()['code']) == 200:
        data = res.json()
        test = requests.get(
            'http://{}-{}.{}/instance/status'.format(
                container['name'],
                user['username'],
                app.config['TOOL_SERVER']
            )
        )
        cpu_usage = float(data['data']['stats']['cpu_usage']) / float(container['cpu']) * 100.0
        if cpu_usage > 100:
            cpu_usage = 100
        app.config['STATISTIC_COLLECTION'].insert(
            {
                "container_id": container['_id'],
                "response_time": test.elapsed.total_seconds(),
                "time": time.time(),
                "ram_usage": data['data']['stats']['mem_usage'],
                "cpu_usage": cpu_usage
            })
        msg = "container={} id={} cpu_usage={} response_time={}".format(
            container['name'],
            str(container['_id']),
            cpu_usage,
            test.elapsed.total_seconds()
        )
        print(msg)

