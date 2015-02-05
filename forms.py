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
    SelectField,
    validators
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError
)

from models import *

class LoginForm(Form):
    email = wtforms.TextField('Email', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])
    password_hash = None
    user = None

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        try:
            user = User.get(User.email==self.email.data)
            print user.password
            print self.password
            print generate_password_hash(self.password.data)
        except DoesNotExist:
            print 'Nope'
            return False
        
        if check_password_hash(user.password, self.password.data):
            return True
        return False

class LogoutForm(Form):
    pass

class PostForm(Form):
    title = wtforms.TextField('Post title', [InputRequired()])
    description = wtforms.TextAreaField('Post description', [InputRequired()])
    correct_solution = wtforms.TextField('Correct solution', [])
    level = wtforms.TextField('Level', [])
    points = wtforms.TextField('Points', [])
    problem_type = wtforms.RadioField(
        'Problem Type',
        [],
        choices=[('regular', 'Regular'), ('bonus', 'Bonus')]
    )

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        return True

class CommentForm(Form):
    description = wtforms.TextAreaField('Comment', [InputRequired()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        return True

class PasswordForm(Form):
    password = PasswordField( 'Password', [validators.InputRequired()])
    password_again = PasswordField( 'Password Again', [validators.InputRequired(), EqualTo(password, message='Passwords must be equal') ])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if self.password.data != self.password_again.data:
            return False
            # raise ValidationError('Passwords dont match')
        return True

class ProfileForm(Form):
    name = wtforms.TextField( 'Name', [ validators.InputRequired() ])
    college = wtforms.TextField( 'College', [ validators.InputRequired() ])
    city = wtforms.TextField( 'City', [ validators.InputRequired() ])
    register_no = wtforms.TextField( 'Register no', [ validators.InputRequired() ])
    phone = wtforms.TextField( 'Phone', [ validators.InputRequired() ])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        return True

class RegistrationForm(Form):
    name = wtforms.TextField( 'Name', [ validators.InputRequired() ])
    email = wtforms.TextField( 'Email', [ validators.InputRequired(), Email(message='Enter a proper email ID') ])
    password = PasswordField( 'Password', [ validators.InputRequired() ])
    password_again = PasswordField( 'Password Again', [ validators.InputRequired(), EqualTo(password, message='Passwords must be equal') ])
    college = wtforms.TextField( 'College', [ validators.InputRequired() ])
    city = wtforms.TextField( 'City', [ validators.InputRequired() ])
    register_no = wtforms.TextField( 'Register no', [ validators.InputRequired() ])
    phone = wtforms.TextField( 'Phone', [ validators.InputRequired() ])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate_email(self):
        try:
            User.get(email=self.email.data)
            raise ValidationError('Email ID is already registered')
        except DoesNotExist:
            if self.password.data != self.password_again.data:
                raise ValidationError('Passwords dont match')
            return True

    def validate(self):
        self.validate_email()
        return True

class SubmissionForm(Form):
    solution = wtforms.TextField('Solution')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        return True
