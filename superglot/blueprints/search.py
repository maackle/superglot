from flask import Blueprint, render_template, current_app as app
from flask.ext.login import current_user, login_required

from superglot import core

blueprint = Blueprint('search', __name__, template_folder='templates')


@blueprint.route('/')
@login_required
def home():
    results = core.find_all_articles(current_user)
    return render_template('views/search/home.jade', articles=results)


@blueprint.route('/relevant')
@login_required
def relevant():
    results = core.find_relevant_articles(current_user)
    return render_template('views/search/home.jade', articles=results)
