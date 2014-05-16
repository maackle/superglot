import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request, redirect, session, flash, url_for, g
from flask.ext.assets import Environment, Bundle
from flask.ext.login import current_user
import requests
import mongoengine
from flask.ext.mongoengine import MongoEngine

from views.api import blueprint as api
from views.chrome_api import blueprint as chrome_api
from views.auth import login_manager, blueprint as auth
from views.frontend import blueprint as frontend
from models import User
from cache import cache


requests.packages.urllib3.add_stderr_logger()

app = Flask(__name__)

app.config.from_object('config.settings')
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(chrome_api, url_prefix='/chrome')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(frontend, url_prefix='')

assets = Environment(app)
assets.url = app.static_url_path

cache.init_app(app, config={
	'CACHE_TYPE': 'filesystem',
	'CACHE_DIR': '.flask-cache',
	'CACHE_THRESHOLD': 1000000,
	'CACHE_DEFAULT_TIMEOUT': 60*60*60*24,  # one day
	})

# mongoengine.connect('superglot')
db = MongoEngine(app)

login_manager.init_app(app)

@app.route('/')
def home():
	return redirect(url_for('frontend.home'))

@app.route('/login/')
def login():
	return redirect(url_for('auth.login'))

@app.route('/logout/')
def logout():
	return redirect(url_for('auth.logout'))


if __name__ == '__main__':
	handler = RotatingFileHandler("log/error.log", maxBytes=10000000, backupCount=10)
	handler.setLevel(logging.WARNING)
	app.logger.addHandler(handler)

	app.run(debug=True, port=31337)