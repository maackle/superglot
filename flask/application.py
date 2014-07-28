import logging
from logging.handlers import RotatingFileHandler

import requests
import mongoengine
from flask import Flask, render_template, request, redirect, session, flash, url_for, g
from flask.ext.assets import Environment, Bundle
from flask.ext.login import current_user
from flask.ext.mongoengine import MongoEngine
from flask.ext.babel import Babel

from controllers.api import blueprint as api
from controllers.chrome_api import blueprint as chrome_api
from controllers.auth import login_manager, blueprint as auth
from controllers.frontend import blueprint as frontend
from controllers.user import blueprint as user_blueprint
from models import User
from cache import cache


requests.packages.urllib3.add_stderr_logger()

app = Flask(__name__)

app.config.from_object('config.settings')
try:
	app.config.from_envvar('SUPERGLOT_SETTINGS')
	print("Loaded config from envvar SUPERGLOT_SETTINGS")
except:
	app.config.from_object('config.development')
	print("Loaded DEVELOPMENT config")

app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(chrome_api, url_prefix='/chrome')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(frontend, url_prefix='')
app.register_blueprint(user_blueprint, url_prefix='/user')

assets = Environment(app)
assets.url = app.static_url_path

babel = Babel(app)

cache.init_app(app, config={
	'CACHE_TYPE': 'filesystem',
	'CACHE_DIR': '.flask-cache',
	'CACHE_THRESHOLD': 1000000,
	'CACHE_DEFAULT_TIMEOUT': 60*60*60*24,  # one day
	})

# mongoengine.connect('superglot')
db = MongoEngine(app)

login_manager.init_app(app)


@app.context_processor
def add_modules():
	import formatting

	return {
		'formatting': formatting,
	}

@app.context_processor
def add_translation():
	from flask.ext.babel import gettext, ngettext

	return {
		'_': gettext,
		'__': ngettext,
	}

@app.context_processor
def add_settings():
	return {
		'settings': dict(app.config),
	}

@app.route('/')
def home():
	return redirect(url_for('frontend.home'))

@app.route('/login/')
def login():
	return redirect(url_for('auth.login'))

@app.route('/logout/')
def logout():
	return redirect(url_for('auth.logout'))

@babel.localeselector
def get_locale():
	if current_user.is_authenticated():
		locale = current_user.native_language
	else:
		locale = request.accept_languages.best_match(app.config['TARGET_LANGUAGES'])
	return locale.split('-')[0]

if __name__ == '__main__':
	handler = RotatingFileHandler("log/error.log", maxBytes=10000000, backupCount=10)
	handler.setLevel(logging.WARNING)
	app.logger.addHandler(handler)

	app.run(debug=True, port=31337)