from flask import Blueprint, render_template
from flask.ext.login import current_user

blueprint = Blueprint('frontend', __name__, template_folder='templates')


@blueprint.route('/')
def home():
    if current_user.is_authenticated():
        return render_template('views/user/dashboard.jade')
    else:
        return render_template('views/home.jade')
