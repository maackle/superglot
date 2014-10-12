from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, HiddenField, FieldList, IntegerField
from wtforms import validators
from wtforms_alchemy import model_form_factory
# from wtforms.validators import Length, EqualTo, InputRequired, Optional, ValidationError, URL
from flask.ext.babel import lazy_gettext as _#, ngettext as __

from database import db

from models import User

BaseModelForm = model_form_factory(Form)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session

required = validators.InputRequired("This field is required")

email_field = StringField(u'Email', [
    required, 
    validators.Length(min=3, max=128)
    ])

password_field = PasswordField('Password', [
        required, 
        validators.Length(min=1, max=32)
        ])


class AddArticleForm(Form):
    title = StringField(_('title'))
    url = StringField(_('URL'), [
        validators.Optional(),
        validators.URL()
        ])
    plaintext = TextAreaField(_('text'))


class LoginForm(ModelForm):
    class Meta:
        model = models.User
        include = ['email', 'password']


class RegisterForm(ModelForm):
    class Meta:
        model = models.User
        include = ['email', 'password', 'native_language', 'target_language']


class UserSettings(ModelForm):
    class Meta:
        model = models.User
        include = ['email', 'native_language', 'target_language']

