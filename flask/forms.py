from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, HiddenField, FieldList, IntegerField
from wtforms.validators import Length, EqualTo, InputRequired, Optional, ValidationError, URL

required = InputRequired("This field is required")

email_field = StringField(u'Email', [
    required, 
    Length(min=3, max=128)
    ])

password_field = PasswordField('Password', [
        required, 
        Length(min=1, max=32)
        ])

class LoginForm(Form):
    email = email_field
    password = password_field


class RegisterForm(Form):
    email = email_field
    password = password_field


class AddDocumentForm(Form):
    url = StringField('URL', [
        URL()
        ])