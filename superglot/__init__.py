
from flask import Flask, request, redirect, url_for
from flask.ext.assets import Environment
from flask.ext.babel import Babel
from flask.ext.login import current_user
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

from superglot.elasticsearch import get_es_client
from superglot.cache import cache


def setup_blueprints(app):

    from superglot.blueprints.frontend import blueprint as frontend
    from superglot.blueprints.auth import blueprint as auth

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(frontend, url_prefix='/app')

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
    app.config.from_object('superglot.config.settings')
    db = SQLAlchemy(app)
    es = get_es_client()
    app.db = db
    app.es = es

    # try:
    #   app.config.from_envvar('SUPERGLOT_SETTINGS')
    #   print("Loaded config from envvar SUPERGLOT_SETTINGS")
    # except:
    #   app.config.from_object('config.development')
    #   print("Loaded DEVELOPMENT config")

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
        from superglot import util, formatting

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
