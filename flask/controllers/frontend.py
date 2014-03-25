from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import current_user

from forms import AddDocumentForm
from models import User
from controllers import api
import nlp
import util

blueprint = Blueprint('frontend', __name__, template_folder='templates')

@blueprint.route('/')
def home():
	return render_template('home.jade')

@blueprint.route('/docs/add/', methods=['GET', 'POST'])
def document_create():
	form = AddDocumentForm(url='http://michaeldougherty.info')
	if form.validate_on_submit():
		text = util.get_remote_text(form.url.data)
		lemmata = set(nlp.lemmatize(text))
		for lemma in lemmata:
			current_user.lemmata.add(lemma)
		current_user.save()
	else:
		return render_template('frontend/document_create.jade', form=form)


@blueprint.route('/docs/', methods=['GET', 'POST'])
def document_list():
	
	return render_template('frontend/document_list.jade')