import time
import datetime
import threading
import requests
import json

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
                    t.join()
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
        for line in data['data']['logs']:
            line = json.loads(line.strip('\n'))
            line['msec'] = int(float(line['msec']))
            line['request_time'] = float(line['request_time'])
            line['container_id'] = container['_id']
            app.config['CONTAINER_LOG_COLLECTION'].insert(line)
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


def nginx_logs_stats():
    threads = []
    users = app.config['USERS_COLLECTION'].find({})
    for user in users:
        containers = app.config['CONTAINERS_COLLECTION'].find({"user_id": user['_id']})
        for container in containers:
            if container['status'] == 'online':
                try:
                    t = threading.Thread(target=logs_processor, args=(user, container))
                    t.start()
                    t.join()
                    threads.append(t)
                except:
                    print "thread error"
            else:
                print 'error'
    for t in threads:
        t.join()


def logs_processor(user, container):
    now = datetime.datetime.now()
    end_time = 24
    i = 1
    start = time.mktime(now.replace(hour=00, minute=00, second=00, microsecond=0).timetuple())
    end = time.mktime(now.replace(hour=1, minute=00, second=00, microsecond=0).timetuple())
    while True:
        r_sum = float(0)
        r_count = 0
        stats = app.config['CONTAINER_LOG_COLLECTION'].find({
            'container_id': container['_id'],
            'msec': {'$gte': start, '$lte': end}
        })
        stats_in = app.config['CONTAINER_PROCESSED_LOG_COLLECTION'].find_one({
            'container_id': container['_id'],
            'time': {'$gte': start, '$lte': end}
        })
        if stats.count() > 0:
            if stats_in:
                stats_in['requests'] = stats.count() + int(stats_in['requests'])
                for stat in stats:
                    r_sum += stat['request_time']
                stats_in['sum'] = stats_in['sum'] + r_sum
                stats_in['avg'] = float(stats_in['sum']) / float(stats_in['requests'])
                stats_in['throughput'] = round(stats_in['requests'] / 60.0, 3)
                app.config['CONTAINER_PROCESSED_LOG_COLLECTION'].save(stats_in)
            else:
                r_count = stats.count()
                for stat in stats:
                    r_sum += stat['request_time']
                avg = r_sum / float(stats.count())
                throughput = round(stats.count() / 60.0, 3)
                app.config['CONTAINER_PROCESSED_LOG_COLLECTION'].insert({
                    "container_id": container['_id'],
                    "requests": r_count,
                    'sum': r_sum,
                    'avg': avg,
                    'throughput': throughput,
                    'time': start + 1800
                })
            app.config['CONTAINER_LOG_COLLECTION'].remove({
                'container_id': container['_id'],
                'msec': {'$gte': start, '$lte': end}
            })

        msg = "container={} id={} time {} - {}".format(
            container['name'],
            str(container['_id']),
            i,
            i - 1
        )
        print(msg)

        i += 1
        if i > end_time:
            break
        if i == end_time:
            start = time.mktime(now.replace(hour=i - 1, minute=00, second=00, microsecond=0).timetuple())
            end = time.mktime(now.replace(hour=i - 1, minute=59, second=59, microsecond=999999).timetuple())
        else:
            start = time.mktime(now.replace(hour=i - 1, minute=00, second=00, microsecond=0).timetuple())
            end = time.mktime(now.replace(hour=i, minute=00, second=00, microsecond=0).timetuple())


def process_logs_stats():
    threads = []
    users = app.config['USERS_COLLECTION'].find({})
    for user in users:
        containers = app.config['CONTAINERS_COLLECTION'].find({"user_id": user['_id']})
        for container in containers:
            if container['status'] == 'online':
                try:
                    t = threading.Thread(target=stats_processor, args=(user, container))
                    t.start()
                    t.join()
                    threads.append(t)
                except:
                    print "thread error"
            else:
                print 'error'
    for t in threads:
        t.join()


def stats_processor(user, container):
    now = datetime.datetime.now()
    end_time = 24
    i = 1
    start = time.mktime(now.replace(hour=00, minute=00, second=00, microsecond=0).timetuple())
    end = time.mktime(now.replace(hour=1, minute=00, second=00, microsecond=0).timetuple())
    while True:
        ram_usage = float(0)
        r_count = 0
        cpu_usage = float(0)
        request_time = float(0)
        stats = app.config['STATISTIC_COLLECTION'].find({
            'container_id': container['_id'],
            'time': {'$gte': start, '$lte': end}
        })
        stats_in = app.config['CONTAINER_PROCESSED_STATS_COLLECTION'].find_one({
            'container_id': container['_id'],
            'time': {'$gte': start, '$lte': end}
        })
        if stats.count() > 0:
            if stats_in:
                for stat in stats:
                    request_time += stat['response_time']
                    cpu_usage += stat['cpu_usage']
                    ram_usage += stat['ram_usage']
                stats_in['requests'] = stats_in['requests'] + stats.count()
                stats_in['cpu_usage'] = stats_in['cpu_usage'] + cpu_usage
                stats_in['ram_usage'] = stats_in['ram_usage'] + ram_usage
                stats_in['request_time'] = stats_in['request_time'] + request_time

                stats_in['request_time_avg'] = stats_in['request_time'] / float(stats_in['requests'])
                stats_in['cpu_usage_avg'] = stats_in['cpu_usage'] / float(stats_in['requests'])
                stats_in['ram_usage_avg'] = stats_in['ram_usage'] / float(stats_in['requests'])

                app.config['CONTAINER_PROCESSED_STATS_COLLECTION'].save(stats_in)
            else:
                r_count = stats.count()
                for stat in stats:
                    request_time += stat['response_time']
                    cpu_usage += stat['cpu_usage']
                    ram_usage += stat['ram_usage']
                app.config['CONTAINER_PROCESSED_STATS_COLLECTION'].insert({
                    "container_id": container['_id'],
                    "requests": r_count,
                    'request_time': request_time,
                    'request_time_avg': request_time / float(r_count),
                    'cpu_usage': cpu_usage,
                    "cpu_usage_avg": cpu_usage / float(r_count),
                    'ram_usage': ram_usage,
                    'ram_usage_avg': ram_usage / float(r_count),
                    'time': start + 1800
                })
            app.config['STATISTIC_COLLECTION'].remove({
                'container_id': container['_id'],
                'time': {'$gte': start, '$lte': end}
            })

        msg = "stats container={} id={} time {} - {}".format(
            container['name'],
            str(container['_id']),
            i,
            i - 1
        )
        print(msg)

        i += 1
        if i > end_time:
            break
        if i == end_time:
            start = time.mktime(now.replace(hour=i - 1, minute=00, second=00, microsecond=0).timetuple())
            end = time.mktime(now.replace(hour=i - 1, minute=59, second=59, microsecond=999999).timetuple())
        else:
            start = time.mktime(now.replace(hour=i - 1, minute=00, second=00, microsecond=0).timetuple())
            end = time.mktime(now.replace(hour=i, minute=00, second=00, microsecond=0).timetuple())
