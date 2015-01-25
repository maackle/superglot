from flask import Blueprint, render_template


blueprint = Blueprint('frontend', __name__, template_folder='templates')


@blueprint.route('/')
def home():
    return render_template('views/home.jade')
