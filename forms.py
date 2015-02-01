from flask import session
from flask.ext.bcrypt import check_password_hash, generate_password_hash
from flask.ext.wtf import Form, RecaptchaField
import wtforms
from wtforms import (
    TextField,
    PasswordField,
    TextAreaField,
    FileField,
    BooleanField,
    HiddenField,
    SelectField
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    InputRequired,
    Length,
    NumberRange,
    Optional
)

from models import *

class LoginForm(Form):
    email = wtforms.TextField('Email', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    password_hash = None
    user = None

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        return True

class LogoutForm(Form):
    pass

class RegistrationForm(Form):
    name = wtforms.TextField(
        'Name',
        [
            DataRequired()
        ]
    )
    email = wtforms.TextField(
        'Email',
        [
            DataRequired(),
            Email(message='Enter a proper email ID')
        ]
    )
    password = PasswordField(
        'Password',
        [
            DataRequired()
        ]
    )
    password_again = PasswordField(
        'Password Again',
        [
            DataRequired(),
            EqualTo(password, message='Passwords must be equal')
        ]
    )

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate_email(self):
        try:
            User.get(email==self.email.data)
        except DoesNotExist:
            return True
        raise ValidationError('Email ID is already registered')

    def validate(self):
        self.validate_email()
        return True
