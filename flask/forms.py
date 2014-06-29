from flask.ext.wtf import Form
from flask.ext.mongoengine.wtf import model_form
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, HiddenField, FieldList, IntegerField
from wtforms import validators
# from wtforms.validators import Length, EqualTo, InputRequired, Optional, ValidationError, URL

from models import User

required = validators.InputRequired("This field is required")

email_field = StringField(u'Email', [
    required, 
    validators.Length(min=3, max=128)
    ])

password_field = PasswordField('Password', [
        required, 
        validators.Length(min=1, max=32)
        ])

LoginForm = model_form(User, Form, only=('email', 'password',))
RegisterForm = model_form(User, Form, only=('email', 'password', 'target_language'))

# class LoginForm(Form):
#     email = email_field
#     password = password_field


# class RegisterForm(Form):
#     email = email_field
#     password = password_field


class AddArticleForm(Form):
    url = StringField('URL', [
        validators.URL()
        ])
    title = StringField('Title')