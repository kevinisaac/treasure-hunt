from flask import (
    Flask,
    redirect,
    render_template,
    url_for
)
from flask.ext.login import (
    LoginManager,
    login_required,
    logout_user
)
from forms import LoginForm, RegistrationForm
from models import *

app = Flask(__name__)
app.secret_key = 'dfsgdfgdfgdf'
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return User.get(id==userid)

# Routes
@app.route('/')
def index():
    """Home page"""
    return 'Hello there..'

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html', login_form=LoginForm())

@app.route('/logout')
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/register')
def register():
    """Registration page"""
    return render_template('register.html', registration_form=RegistrationForm())

@app.route('/post/<int:id>/<slug>')
@login_required
def post(id, slug):
    """Post page"""
    return 'Post page'
