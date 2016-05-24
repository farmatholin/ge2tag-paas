import datetime

import requests
import time
from bson import ObjectId
from flask import request, redirect, render_template, url_for, flash, g, jsonify
from flask.ext.login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

from app import app, lm
from app.models.container import Container, CONTAINER__STATUS_OFFLINE, CONTAINER__STATUS_ONLINE
from app.models.user import User
from .forms import LoginForm, SignUpForm, CreateContainer


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['USERS_COLLECTION'].find_one({"username": form.username.data})
        if user and User.validate_login(user['password'], form.password.data):
            user_obj = User(str(user['_id']), user['username'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("containers"))
        flash("Wrong username or password!", category='error')
    return render_template('user/login.html', title='login', form=form)


@app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    form = SignUpForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['USERS_COLLECTION'].find_one({"username": form.username.data})
        if not user:
            pass_hash = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            user_id = app.config['USERS_COLLECTION'].insert({"username": form.username.data, "password": pass_hash})
            user_obj = User(str(user_id), form.username.data)
            login_user(user_obj)
            flash("Account created in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("containers"))
        flash("Wrong username or password!", category='error')
    return render_template('user/signUp.html', title='Sign Up', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/user/containers')
@login_required
def containers():
    containers_raw = app.config['CONTAINERS_COLLECTION'].find({"user_id": ObjectId(g.user.get_id())})

    return render_template(
        'user/containers_list.html',
        title='Containers',
        containers=Container.get_containers_list(containers_raw)
    )


@app.route('/user/containers/create', methods=['GET', 'POST'])
@login_required
def create_container():
    form = CreateContainer()
    if request.method == 'POST' and form.validate_on_submit():
        cont = app.config['CONTAINERS_COLLECTION'].find_one(
            {
                "name": form.name.data,
                "user_id": ObjectId(g.user.user_id)
            }
        )
        if not cont:
            res = requests.post(
                'http://{}:{}/create'.format(
                    app.config['TOOL_SERVER'], app.config['TOOL_PORT'])
                , json={
                    "container": form.name.data,
                    "user": g.user.username,
                    "cpu": form.cpu.data,
                    "ram": form.ram.data,
                }
            )
            if res.ok and int(res.json()['code']) == 200:
                data = res.json()
                app.config['CONTAINERS_COLLECTION'].insert(
                    {
                        "name": form.name.data,
                        "user_id": ObjectId(g.user.user_id),
                        'host': data['data']['host'],
                        'status': CONTAINER__STATUS_OFFLINE,
                        "cpu": form.cpu.data,
                        "ram": form.ram.data,
                    }
                )
                flash("Container Created", category='success')
                return redirect(request.args.get("next") or url_for("containers"))
            else:
                flash("Container create fail", category='error')
        flash("Container already exist", category='error')
    return render_template('user/create_container.html', title='Create Container', form=form)


@app.route('/user/container/<container_id>')
@login_required
def container(container_id):
    cont = app.config['CONTAINERS_COLLECTION'].find_one(
        {
            "name": container_id,
            "user_id": ObjectId(g.user.get_id())
        }
    )
    return render_template('user/container.html', container=cont)



@app.route('/user/container/stats/hourly/<type>/<container_id>')
@login_required
def container_stats_hourly(type, container_id):
    cont = app.config['CONTAINERS_COLLECTION'].find_one(
        {
            "name": container_id,
            "user_id": ObjectId(g.user.get_id())
        }
    )
    now = datetime.datetime.now()
    end_time = 24
    i = 1
    start = time.mktime(now.replace(hour=00, minute=00, second=00, microsecond=0).timetuple())
    end = time.mktime(now.replace(hour=1, minute=00, second=00, microsecond=0).timetuple())
    total_sum = float()
    total_count = float()
    hours = 0
    res = {
        'labels': [],
        'data': {
            'avg': [],
        },
        'total_avg': 0,
    }
    label = "{} - {}".format(0, 1)
    label_type = ''
    label_type_avg = ''
    if type == 'cpu':
        label_type = 'cpu_usage'
        label_type_avg = 'cpu_usage_avg'
    elif type == 'response':
        label_type = 'request_time'
        label_type_avg = 'request_time_avg'
    elif type == 'ram':
        label_type = 'ram_usage'
        label_type_avg = 'ram_usage_avg'
    while True:
        stats = app.config['CONTAINER_PROCESSED_STATS_COLLECTION'].find_one({
            'container_id': cont['_id'],
            'time': {'$gte': start, '$lte': end}
        })
        res['labels'].append(label)
        if stats:
            res['data']['avg'].append(round(stats[label_type_avg], 3))
            total_sum += stats[label_type]
            total_count += stats['requests']
            hours += 1
        else:
            res['data']['avg'].append(0)

        i += 1
        if i > end_time:
            break
        if i == end_time:
            start = time.mktime(now.replace(hour=i-1, minute=00, second=00, microsecond=0).timetuple())
            end = time.mktime(now.replace(hour=i-1, minute=59, second=59, microsecond=999999).timetuple())
            label = "{} - {}".format(i-1, 24)
        else:
            start = time.mktime(now.replace(hour=i - 1, minute=00, second=00, microsecond=0).timetuple())
            end = time.mktime(now.replace(hour=i, minute=00, second=00, microsecond=0).timetuple())
            label = "{} - {}".format(i - 1, i)
    if total_count > 0:
        res['total_avg'] = round(total_sum / total_count, 4)

    return jsonify(res)


@app.route('/user/container/log/hourly/response/<container_id>')
@login_required
def container_log_hourly_response(container_id):
    cont = app.config['CONTAINERS_COLLECTION'].find_one(
        {
            "name": container_id,
            "user_id": ObjectId(g.user.get_id())
        }
    )
    now = datetime.datetime.now()
    end_time = 24
    i = 1
    start = time.mktime(now.replace(hour=00, minute=00, second=00, microsecond=0).timetuple())
    end = time.mktime(now.replace(hour=1, minute=00, second=00, microsecond=0).timetuple())
    total_sum = float()
    total_count = float()
    hours = 0
    normal = 0
    res = {
        'labels': [],
        'data': {
            'avg': [],
            'requests': [],
            'throughput': [],
            'normal': []
        },
        'total_avg': 0,
        'total_req': 0,
        'normal': 0,
        'total_throughput': 0
    }
    label = "{} - {}".format(0, 1)
    while True:
        r_sum = float(0)
        stats = app.config['CONTAINER_PROCESSED_LOG_COLLECTION'].find_one({
            'container_id': cont['_id'],
            'time': {'$gte': start, '$lte': end}
        })
        res['labels'].append(label)
        if stats:
            res['data']['requests'].append(stats['requests'])
            res['data']['avg'].append(round(stats['avg'], 3))
            res['data']['throughput'].append(round(stats['throughput']/60, 3))
            res['data']['normal'].append(round(1/stats['avg']))
            normal += round(1/stats['avg'])
            hours += 1
            total_sum += stats['sum']
            total_count += stats['requests']
        else:
            res['data']['avg'].append(0)
            res['data']['requests'].append(0)
            res['data']['throughput'].append(0)
            res['data']['normal'].append(0)

        i += 1
        if i > end_time:
            break
        if i == end_time:
            start = time.mktime(now.replace(hour=i - 1, minute=00, second=00, microsecond=0).timetuple())
            end = time.mktime(now.replace(hour=i - 1, minute=59, second=59, microsecond=999999).timetuple())
            label = "{} - {}".format(i - 1, 24)
        else:
            start = time.mktime(now.replace(hour=i - 1, minute=00, second=00, microsecond=0).timetuple())
            end = time.mktime(now.replace(hour=i, minute=00, second=00, microsecond=0).timetuple())
            label = "{} - {}".format(i - 1, i)
    if total_count > 0:
        res['total_avg'] = round(total_sum / total_count, 4)
        res['total_ms'] = total_sum
        res['total_req'] = total_count
        res['total_throughput'] = round(total_count / 60, 3)
        if hours > 0:
            res['normal'] = round(normal/hours)

    return jsonify(res)


@app.route('/user/container/cmd/<container_id>/<cmd>', methods=['POST'])
@login_required
def container_cmd(container_id, cmd):
    cont = app.config['CONTAINERS_COLLECTION'].find_one(
        {
            "name": container_id,
            "user_id": ObjectId(g.user.get_id())
        }
    )
    if cont:
        if cmd == 'start' and cont['status'] == CONTAINER__STATUS_OFFLINE:
            res = requests.post(
                'http://{}:{}/start'.format(
                    app.config['TOOL_SERVER'], app.config['TOOL_PORT'])
                , json={
                    "container": cont['name'],
                    "user": g.user.username
                }
            )
            if res.ok and int(res.json()['code']) == 200:
                app.config['CONTAINERS_COLLECTION'].update(
                    {"_id": cont['_id']},
                    {'$set': {'status': CONTAINER__STATUS_ONLINE}}
                )
                return jsonify({
                    "code": 200,
                    "message": "ok"
                })
        elif cmd == 'stop' and cont['status'] == CONTAINER__STATUS_ONLINE:
            res = requests.post(
                'http://{}:{}/stop'.format(
                    app.config['TOOL_SERVER'], app.config['TOOL_PORT'])
                , json={
                    "container": cont['name'],
                    "user": g.user.username
                }
            )
            if res.ok and int(res.json()['code']) == 200:
                app.config['CONTAINERS_COLLECTION'].update(
                    {"_id": cont['_id']},
                    {'$set': {'status': CONTAINER__STATUS_OFFLINE}}
                )
                return jsonify({
                    "code": 200,
                    "message": "ok"
                })
        elif cmd == 'remove':
            res = requests.post(
                'http://{}:{}/remove'.format(
                    app.config['TOOL_SERVER'], app.config['TOOL_PORT'])
                , json={
                    "container": cont['name'],
                    "user": g.user.username
                }
            )
            if res.ok and int(res.json()['code']) == 200:
                app.config['CONTAINERS_COLLECTION'].remove(
                    {"_id": cont['_id']},
                )
                app.config['STATISTIC_COLLECTION'].remove(
                    {"container_id": cont['_id']},
                )
                app.config['CONTAINER_PROCESSED_LOG_COLLECTION '].remove(
                    {"container_id": cont['_id']},
                )
                app.config['CONTAINER_LOG_COLLECTION'].remove(
                    {"container_id": cont['_id']},
                )
                return jsonify({
                    "code": 200,
                    "message": "ok"
                })
        else:
            pass
    return jsonify({
        "code": 400,
        "message": "cmd error"
    })


@app.before_request
def before_request():
    g.user = current_user


@lm.user_loader
def load_user(user_id):
    u = app.config['USERS_COLLECTION'].find_one({"_id": ObjectId(user_id)})
    if not u:
        return None
    return User(u['_id'], u['username'])
