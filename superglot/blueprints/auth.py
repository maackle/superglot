from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app as app
from flask.ext.login import login_user, logout_user, login_required
from flask.ext.babel import gettext as _

from superglot.forms import LoginForm, RegisterForm
from superglot import core

blueprint = Blueprint('auth', __name__, template_folder='templates')

@blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    ctx = dict(form=form)
    template = "views/auth/login.jade"
    if request.method=='POST':
        if form.validate_on_submit():
            data = form.data
            user = core.authenticate_user(**data)
            if user:
                result = login_user(user, remember=False)
                flash(_("Logged in successfully.").capitalize())
                return redirect(request.args.get("next") or url_for("home"))
            else:
                flash(_("Invalid username or password.").capitalize(), 'danger')
                return render_template(template, **ctx)
        else:
            flash(_('There was a problem logging in. Please contact support at %(email)s.', email=app.config['EMAIL_SUPPORT']), 'danger')
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
            (user, created) = core.register_user(email=data['email'], password= data['password'])
            if created:
                flash(_("You're all signed up! Now you can log in."))
                return redirect(url_for('auth.login'))
            else:
                flash(_("An account with this email address already exists."), 'danger')
                return render_template(template, form=form)
        else:
            app.logger.error(form.errors)
            flash(_('Uh oh, there was a problem with your registration. Please email %(email)s', email=app.config['EMAIL_SUPPORT']), 'danger')
            return render_template(template, form=form)
    else:
        return render_template(template, form=form)
