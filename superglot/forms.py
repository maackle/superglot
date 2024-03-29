from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, HiddenField, FieldList, IntegerField
from wtforms import validators
from wtforms_alchemy import model_form_factory, ModelFormField
# from wtforms.validators import Length, EqualTo, InputRequired, Optional, ValidationError, URL
from flask.ext.babel import lazy_gettext as _

from superglot import database as db
from superglot import models

BaseModelForm = model_form_factory(Form)

required = validators.InputRequired("This field is required")

email_field = StringField(u'Email', [
    required,
    validators.Length(min=3, max=128)
    ])

password_field = PasswordField('Password', [
        required,
        validators.Length(min=1, max=32)
        ])


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.Session()


class AddArticleForm(Form):
    title = StringField(_('title'))
    url = StringField(_('URL'), [
        validators.Optional(),
        validators.URL()
        ])
    plaintext = TextAreaField(_('text'))


class SearchArticleForm(Form):
    title = StringField(_('title'))


class LanguageForm(ModelForm):
    class Meta:
        model = models.Language
        include = ['code']


class LoginForm(ModelForm):
    class Meta:
        model = models.User
        only = ['email', 'password']


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
