import requests
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
                    "user": g.user.username
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
                    {'$set':{'status': CONTAINER__STATUS_ONLINE}}
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
