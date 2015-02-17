from flask import Blueprint, render_template, current_app as app
from flask.ext.login import current_user, login_required

from superglot import core

blueprint = Blueprint('test', __name__, template_folder='templates')


@blueprint.route('/annotate')
@login_required
def annotate():
    results = core.find_all_articles(current_user)
    return render_template('views/test/annotate.jade', articles=results)
