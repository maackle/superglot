import re
from bs4 import BeautifulSoup
import requests

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import current_user, login_required
from flask.ext.babel import lazy_gettext as _
from mongoengine.errors import NotUniqueError

from forms import UserSettingsForm
from controllers import api
from util import sorted_words
import nlp
import util
import formatting


blueprint = Blueprint('user', __name__, template_folder='templates')

@blueprint.route('/')
def home():
	return redirect(url_for('.settings'))

@blueprint.route('/settings/', methods=['GET', 'POST'])
def settings():
	form = UserSettingsForm(obj=current_user)

	if form.validate_on_submit():
		current_user.email = form.email.data
		current_user.native_language = form.native_language.data
		current_user.target_language = form.target_language.data
		current_user.save()
		flash(_("settings updated").capitalize(), 'info')
		return redirect(url_for('user.settings'))

	return render_template('views/user/user_settings.jade', form=form)

