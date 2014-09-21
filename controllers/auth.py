from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask.ext.login import LoginManager, login_user, logout_user, login_required
from flask.ext.babel import gettext as _

from forms import LoginForm, RegisterForm
from models import User, UserWordList


login_manager = LoginManager()

@login_manager.user_loader
def load_user(userid):
	user = User.objects(id=userid).first()
	return user

blueprint = Blueprint('auth', __name__, template_folder='templates')

@blueprint.route('/login/', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	ctx = dict(form=form)
	template = "views/auth/login.jade"
	if request.method=='POST':
		if form.validate_on_submit():
			data = form.data
			user = User.authenticate(**data)
			if user:
				result = login_user(user, remember=False)
				flash(_("Logged in successfully.").capitalize())
				return redirect(request.args.get("next") or url_for("home"))
			else:
				flash(_("Invalid username or password.").capitalize(), 'danger')
				return render_template(template, **ctx)
		else:
			flash(_('There was a problem logging in. Please contact support at %(email)s.', current_app.config['EMAIL_SUPPORT']), 'danger')
			return render_template(template, **ctx)
	else:
		return render_template(template, **ctx)

@blueprint.route('/logout/')
@login_required
def logout():
	logout_user()
	flash(_("You are logged out."))
	return redirect(url_for('home'))

@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	template = "views/auth/register.jade"
	if request.method=='POST':
		if form.validate_on_submit():
			data = form.data
			(user, created) = User.objects.get_or_create(
				email=data['email'],
				defaults={
					'password': data['password'],
					'words': UserWordList.default(),
					'native_language': 'en',
				})
			if created:
				flash(_("You're all signed up! Now you can log in."))
				return redirect(url_for('auth.login'))
			else:
				flash(_("An account with this email address already exists."), 'danger')
				return render_template(template, form=form)
		else:
			print(form.data)
			flash(_('Uh oh, there was a problem with your registration. Please email %(email)s', current_app.config['EMAIL_SUPPORT']), 'danger')
			return render_template(template, form=form)
	else:
		return render_template(template, form=form)