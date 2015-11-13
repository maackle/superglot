from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    TextAreaField,
    HiddenField,
    FieldList,
    IntegerField,
    SelectField
)
from wtforms import validators
from wtforms_alchemy import model_form_factory, ModelFormField
# from wtforms.validators import Length, EqualTo, InputRequired, Optional, ValidationError, URL
from flask.ext.babel import lazy_gettext as _
from flask.ext.wtf import Form


from superglot import database as db
from superglot import models
from superglot.config import settings

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
    language = TextAreaField(_('language'))


class SearchArticleForm(Form):
    title = StringField(_('title'))


class LoginForm(ModelForm):
    class Meta:
        model = models.User
        only = ['email', 'password']


class RegisterForm(ModelForm):
    class Meta:
        model = models.User
        only = ['email', 'password', 'target_language']

    target_language = SelectField(choices=settings.TARGET_LANGUAGE_CHOICES)


class UserSettingsForm(ModelForm):
    class Meta:
        model = models.User
        only = ['email', 'target_language', 'native_language']

    native_language = SelectField(choices=settings.NATIVE_LANGUAGE_CHOICES)
    target_language = SelectField(choices=settings.TARGET_LANGUAGE_CHOICES)
