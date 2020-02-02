""" Static views generated for PagerMaid. """

from os.path import join
from pathlib import Path
from os.path import exists
from flask import render_template, request, url_for, redirect, send_from_directory
from flask_login import login_user, logout_user, current_user
from pagermaid.interface import app, login
from pagermaid.interface.modals import User
from pagermaid.interface.forms import LoginForm, SetupForm


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/setup", methods=['GET', 'POST'])
def setup():
    form = SetupForm(request.form)
    msg = None
    if request.method == 'GET':
        if exists('data/.user_configured'):
            return redirect(url_for('login'), code=302)
        return render_template('pages/setup.html', form=form, msg=msg)
    if form.validate_on_submit():
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)
        email = request.form.get('email', '', type=str)
        user = User.query.filter_by(user=username).first()
        user_by_email = User.query.filter_by(email=email).first()
        if user or user_by_email:
            msg = 'This email already exists on this system, sign in if it is yours.'
        else:
            pw_hash = password
            user = User(username, email, pw_hash)
            user.save()
            Path('data/.user_configured').touch()
            return redirect(url_for('login'), code=302)
    else:
        msg = 'Invalid input.'
    return render_template('pages/setup.html', form=form, msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not exists('data/.user_configured'):
        return redirect(url_for('setup'), code=302)
    form = LoginForm(request.form)
    msg = None
    if form.validate_on_submit():
        username = request.form.get('username', '', type=str)
        password = request.form.get('password', '', type=str)
        user = User.query.filter_by(user=username).first()
        if user:
            if user.password == password:
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Incorrect username or password."
        else:
            msg = "This user does not exist."
    return render_template('pages/login.html', form=form, msg=msg)


@app.route('/', defaults={'path': '/index.html'})
@app.route('/<path>')
def index(path):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    try:
        if path.endswith(('.png', '.svg' '.ttf', '.xml', '.ico', '.woff', '.woff2')):
            return send_from_directory(join(app.root_path, 'static'), path)
        return render_template('pages/' + path)
    except BaseException:
        return render_template('layouts/auth-default.html',
                               content=render_template('pages/404.html'))
