import os
import logging
from logging.handlers import RotatingFileHandler
import requests

from flask import Flask, render_template, request, redirect, session, flash, url_for, g
from flask.ext.assets import Environment, Bundle
from flask.ext.login import current_user
from flask.ext.login import LoginManager
from flask.ext.babel import Babel
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

from superglot import elasticsearch
from superglot.cache import cache

def setup_blueprints(app):

	from controllers.api import blueprint as api_blueprint
	from controllers.chrome_api import blueprint as chrome_api_blueprint
	from controllers.auth import blueprint as auth_blueprint
	from controllers.frontend import blueprint as frontend_blueprint
	from controllers.frontend.articles import blueprint as frontend_articles_blueprint
	from controllers.frontend.words import blueprint as frontend_words_blueprint
	from controllers.search import blueprint as search_blueprint
	from controllers.study import blueprint as study_blueprint
	from controllers.user import blueprint as user_blueprint

	app.register_blueprint(api_blueprint, url_prefix='/api')
	app.register_blueprint(chrome_api_blueprint, url_prefix='/chrome')
	app.register_blueprint(auth_blueprint, url_prefix='/auth')
	app.register_blueprint(search_blueprint, url_prefix='/search')
	app.register_blueprint(study_blueprint, url_prefix='/study')
	app.register_blueprint(user_blueprint, url_prefix='/user')
	app.register_blueprint(frontend_blueprint, url_prefix='')
	app.register_blueprint(frontend_articles_blueprint, url_prefix='')
	app.register_blueprint(frontend_words_blueprint, url_prefix='')

	login_manager = LoginManager()
	login_manager.init_app(app)

	@login_manager.user_loader
	def load_user(userid):
		from superglot import models
		user = app.db.session.query(models.User).get(userid)
		return user



def create_app(**extra_config):

	# requests.packages.urllib3.add_stderr_logger()

	app = Flask(__name__)
	app.config.from_object('config.settings')
	db = SQLAlchemy(app)
	es = elasticsearch.get_client()
	app.db = db
	app.es = es

	# try:
	# 	app.config.from_envvar('SUPERGLOT_SETTINGS')
	# 	print("Loaded config from envvar SUPERGLOT_SETTINGS")
	# except:
	# 	app.config.from_object('config.development')
	# 	print("Loaded DEVELOPMENT config")

	app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

	setup_blueprints(app)

	assets = Environment(app)
	assets.url = app.static_url_path

	babel = Babel(app)

	cache.init_app(app, config={
		'CACHE_TYPE': 'filesystem',
		'CACHE_DIR': '.flask-cache',
		'CACHE_THRESHOLD': 1000000,
		'CACHE_DEFAULT_TIMEOUT': 60*60*60*24,  # one day
		})

	toolbar = DebugToolbarExtension(app)

	@app.context_processor
	def add_modules():
		import formatting
		from superglot import util

		return {
			'formatting': formatting,
			'util': util,
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
			locale = request.accept_languages.best_match(app.config['SUPPORTED_TARGET_LANGUAGES'])
		if not locale:
			locale = 'en'
		return locale.split('-')[0]

	return app


if __name__ == '__main__':
	app = create_app()
	handler = RotatingFileHandler("log/error.log", maxBytes=10000000, backupCount=10)
	handler.setLevel(logging.WARNING)
	app.logger.addHandler(handler)

	app.run(debug=True, port=app.config['SERVER_PORT'])