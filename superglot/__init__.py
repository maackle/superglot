
from flask import Flask, request, redirect, url_for
from flask.ext.assets import Environment
from flask.ext.babel import Babel
from flask.ext.login import current_user, LoginManager
from flask.ext.security import Security
from flask_debugtoolbar import DebugToolbarExtension
from flask_jsglue import JSGlue

from superglot.elasticsearch import get_es_client
from superglot.cache import cache
from superglot import models


def setup_blueprints(app):

    from superglot.blueprints.api import blueprint as api_blueprint
    from superglot.blueprints.auth import blueprint as auth_blueprint
    from superglot.blueprints.frontend import blueprint as frontend_blueprint
    from superglot.blueprints.frontend.articles import blueprint as frontend_articles_blueprint
    from superglot.blueprints.frontend.vocab import blueprint as frontend_vocab_blueprint
    from superglot.blueprints.search import blueprint as search_blueprint
    from superglot.blueprints.study import blueprint as study_blueprint
    from superglot.blueprints.user import blueprint as user_blueprint
    from superglot.blueprints.test import blueprint as test_blueprint

    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(auth_blueprint, url_prefix='')
    app.register_blueprint(search_blueprint, url_prefix='/search')
    app.register_blueprint(study_blueprint, url_prefix='/study')
    app.register_blueprint(user_blueprint, url_prefix='/user')
    app.register_blueprint(test_blueprint, url_prefix='/test')
    app.register_blueprint(frontend_blueprint, url_prefix='')
    app.register_blueprint(frontend_articles_blueprint, url_prefix='')
    app.register_blueprint(frontend_vocab_blueprint, url_prefix='')

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(userid):
        user = app.db.session.query(models.User).get(userid)
        return user


def create_app(**extra_config):

    # requests.packages.urllib3.add_stderr_logger()

    app = Flask(__name__)
    app.config.from_object('superglot.config.settings')
    models.db.init_app(app)
    es = get_es_client()
    app.db = models.db
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

    JSGlue(app)  # adds url_for to frontend

    Security(app, models.user_datastore)

    DebugToolbarExtension(app)

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
