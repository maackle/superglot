from flask import Blueprint, render_template
from flask.ext.login import current_user

from superglot import core

blueprint = Blueprint('frontend', __name__, template_folder='templates')


@blueprint.route('/')
def home():
    if current_user.is_authenticated():
        due_vocab = core.gen_due_vocab(current_user)
        ctx = {
            'due_vocab_count': len(due_vocab)
        }
        return render_template('views/user/dashboard.jade', **ctx)
    else:
        return render_template('views/home.jade')
