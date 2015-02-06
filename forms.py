from flask import session, flash
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
    email = wtforms.StringField('Email', [validators.Required(message='Email required')])
    password = PasswordField('Password', [validators.Required()])
    password_hash = None
    user = None

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            flash('Values must be non-empty')
            return False
        # Check if user exists
        try:
            user = User.get(User.email==self.email.data)
        except DoesNotExist:
            flash('No such user registered')
            return False
        
        # Check if password matches
        if not check_password_hash(user.password, self.password.data):
            flash('Wrong password')
            return False
        
        # Check if account is activated
        if user.token != '':
            flash('Check your email (' + user.email + ') to validate your account!')
            return False
        return True

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
    name = wtforms.TextField(
        'Name',
        [
            validators.required(),
            validators.Length(min=2, max=20, message='Names are usually between 2 and 20 characters')
        ]
    )
    email = EmailField(
        'Email',
        [
            validators.InputRequired(),
            Email(message='Enter a proper email ID')
        ]
    )
    password = PasswordField(
        'Password',
        [
            validators.InputRequired(),
            validators.Length(min=6, max=40, message='Password length should be between 6 and 40 characters')
        ]
    )
    password_again = PasswordField(
        'Password Again',
        [
            validators.InputRequired(),
            EqualTo(password, message='Passwords must be equal')
        ]
    )
    college = wtforms.TextField(
        'College',
        [
            validators.InputRequired(),
            validators.Length(min=3, max=100, message='Too short to be a college name')
        ]
    )
    city = wtforms.TextField(
        'City',
        [
            validators.InputRequired(),
            validators.Length(min=3, max=100, message='Too short to be a city name')
        ]
    )
    register_no = wtforms.TextField(
        'Register no',
        [
            validators.InputRequired(),
            validators.Length(min=4, max=100, message='Too short to be a register number')
        ]
    )
    phone = wtforms.TextField(
        'Mobile',
        [
            validators.InputRequired(),
            validators.Length(min=10, max=20, message='Too short to be a phone number')
        ]
    )

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate_email(self):
        try:
            User.get(email=self.email.data)
            flash('Email ID already taken!', 'error')
            return False
            raise ValidationError('Email ID is already registered')
        except DoesNotExist:
            if self.password.data != self.password_again.data:
                flash('Passwords do not match', 'error')
                return False
                raise ValidationError('Passwords dont match')
            return True

    def validate(self):
        if not self.validate_email():
            return False
        return True

class SubmissionForm(Form):
    solution = wtforms.TextField('Solution')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        return True

class UploadForm(Form):
    image = wtforms.FileField('Image')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        return True
