""" PagerMaid web interface utility. """

from threading import Thread
from distutils2.util import strtobool
from importlib import import_module
from cheroot.wsgi import Server as WSGIServer, PathInfoDispatcher
from flask import Flask
from flask.logging import default_handler
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

try:
    from pagermaid import config, working_dir, logs, logging_handler
except ModuleNotFoundError:
    print("This module should not be ran directly.")
    exit(1)

app = Flask("pagermaid")
app.config['CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = config['web_interface']['secret_key']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{working_dir}/data/web_interface.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login = LoginManager()
login.init_app(app)


@app.before_first_request
def init_db():
    db.create_all()


import_module('pagermaid.interface.views')
import_module('pagermaid.interface.modals')

dispatcher = PathInfoDispatcher({'/': app})
server = WSGIServer((config['web_interface']['host'], int(config['web_interface']['port'])), dispatcher)


def start():
    if strtobool(config['web_interface']['enable']):
        logs.info(f"Starting web interface at {config['web_interface']['host']}:{config['web_interface']['port']}")
        app.logger.removeHandler(default_handler)
        app.logger.addHandler(logging_handler)
        try:
            server.start()
        except OSError:
            logs.fatal("Another process is binded to the port PagerMaid needs!")
            return
    else:
        logs.info("Web interface is disabled.")


Thread(target=start).start()
