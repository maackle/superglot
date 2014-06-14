from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask.ext.login import LoginManager, login_user, logout_user, login_required

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
				flash("Logged in successfully.")
				return redirect(request.args.get("next") or url_for("home"))
			else:
				flash("Nope!", 'danger')
				return render_template(template, **ctx)

		else:
			flash('problem logging in', 'danger')
			return render_template(template, **ctx)
	else:
		return render_template(template, **ctx)

@blueprint.route('/logout/')
@login_required
def logout():
	logout_user()
	flash("Logged ya out!")
	return redirect(url_for('home'))

@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if request.method=='POST':
		if form.validate_on_submit():
			data = form.data
			user = User(
				email=data['email'], 
				password=data['password'],
				words=UserWordList.default()).save()
			flash("Created user.")
			return redirect(url_for('auth.login'))
		else:
			print(form.data)
			flash('problem creating user', 'danger')
			return render_template("views/auth/register.jade", form=form)
	else:
		return render_template("views/auth/register.jade", form=form)
