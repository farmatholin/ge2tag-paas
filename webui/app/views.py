from bson import ObjectId
from flask import request, redirect, render_template, url_for, flash, g
from flask.ext.login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

from app import app, lm
from app.models.user import User
from app.models.container import Container
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
            user_obj = User(user_id, form.username.data)
            login_user(user_obj)
            flash("Account created in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("containers"))
        flash("Wrong username or password!", category='error')
    return render_template('user/signUp.html', title='SignUp', form=form)


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
        app.config['CONTAINERS_COLLECTION'].insert(
            {
                "name": form.name.data,
                "user_id": ObjectId(g.user.user_id)
            }
        )
        flash("Container Created", category='success')
        return redirect(request.args.get("next") or url_for("containers"))
    return render_template('user/create_container.html', title='Create Container', form=form)


@app.route('/user/container/<container_id>')
@login_required
def container(container_id):
    return 'a'


@app.before_request
def before_request():
    g.user = current_user


@lm.user_loader
def load_user(user_id):
    u = app.config['USERS_COLLECTION'].find_one({"_id": ObjectId(user_id)})
    if not u:
        return None
    return User(u['_id'], u['username'])
