from flask import session, flash
from flask.ext.bcrypt import check_password_hash, generate_password_hash
from flask.ext.wtf import Form, RecaptchaField
import wtforms
from wtforms import (
    StringField,
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
    email = EmailField('Email', [validators.Required(message='Email required')])
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
    title = wtforms.StringField('Post title', [InputRequired()])
    description = wtforms.TextAreaField('Post description', [InputRequired()])
    correct_solution = wtforms.StringField('Correct solution', [])
    level = wtforms.StringField('Level', [])
    points = wtforms.StringField('Points', [])
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
    password_again = PasswordField( 'Password Again', [validators.InputRequired()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        if self.password.data != self.password_again.data:
            return False
            # raise ValidationError('Passwords dont match')
        return True

class ProfileForm(Form):
    name = wtforms.StringField( 'Name', [ validators.InputRequired() ])
    college = wtforms.StringField( 'College', [ validators.InputRequired() ])
    city = wtforms.StringField( 'City', [ validators.InputRequired() ])
    register_no = wtforms.StringField( 'Register no', [ validators.InputRequired() ])
    phone = wtforms.StringField( 'Phone', [ validators.InputRequired() ])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        return True

class RegistrationForm(Form):
    name = StringField( 'Name', [ validators.Required() ])
    email = EmailField( 'Email', [ validators.Required() ])
    password = PasswordField( 'Password', [ validators.Required() ])
    password_again = PasswordField( 'Password Again', [ validators.Required() ])
    college = StringField(
        'College',
        [
            validators.Required(),
            validators.Length(min=3, max=100, message='Too short to be a college name')
        ]
    )
    city = StringField(
        'City',
        [
            validators.Required(),
            validators.Length(min=3, max=100, message='Too short to be a city name')
        ]
    )
    register_no = StringField(
        'Register no',
        [
            validators.Required(),
            validators.Length(min=4, max=100, message='Too short to be a register number')
        ]
    )
    phone = StringField(
        'Mobile',
        [
            validators.Required(),
            validators.Length(min=10, max=20, message='Too short to be a phone number')
        ]
    )

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            flash('Values must be non-empty')
            return False
        
        try:
            User.get(email=self.email.data)
            flash('Email ID already taken!', 'error')
            return False
        except DoesNotExist:
            if self.password.data != self.password_again.data:
                flash('Passwords do not match', 'error')
                return False
        return True

class SubmissionForm(Form):
    solution = wtforms.StringField('Solution')

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
