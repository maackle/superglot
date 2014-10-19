from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, HiddenField, FieldList, IntegerField
from wtforms import validators
from wtforms_alchemy import model_form_factory, ModelFormField
# from wtforms.validators import Length, EqualTo, InputRequired, Optional, ValidationError, URL
from flask.ext.babel import lazy_gettext as _#, ngettext as __

from relational import models
import database as db

BaseModelForm = model_form_factory(Form)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.Session()

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


class LanguageForm(ModelForm):
    class Meta:
        model = models.Language
        include = ['code']

class LoginForm(ModelForm):
    class Meta:
        model = models.User
        include = ['email', 'password']


class RegisterForm(ModelForm):
    class Meta:
        model = models.User
        include = ['email', 'password']

    target_language = ModelFormField(LanguageForm)


class UserSettingsForm(ModelForm):
    class Meta:
        model = models.User
        include = ['email']

    target_language = ModelFormField(LanguageForm)
    native_language = ModelFormField(LanguageForm)
