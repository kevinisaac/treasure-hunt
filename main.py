from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for
)
from flask.ext.login import (
    current_user,
    LoginManager,
    login_required,
    login_user,
    logout_user
)
from forms import LoginForm, RegistrationForm
from models import *

from core import logout_required

app = Flask(__name__)
app.secret_key = 'dfsgdfgdfgdf'
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return User.get(id=int(userid))

# Routes
@app.route('/')
@login_required
def index():
    """Home page"""
    print current_user.is_authenticated()
    return 'Hello there..'

@app.route('/login', methods=['GET', 'POST'])
# @logout_required('.index')
def login():
    print current_user.is_authenticated()
    """Login page"""
    if request.method == 'GET':
        return render_template('login.html', login_form=LoginForm())
    else:
        login_form = LoginForm(request.form)
        if login_form.validate():
            email = request.form.get('email')
            login_user(User.get(email=email))
            return redirect(request.args.get('next') or url_for('index'))
        return render_template('login.html', login_form=LoginForm())

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    print current_user.is_authenticated()
    return redirect(url_for('index'))

@app.route('/register')
# @logout_required('index')
def register():
    """Registration page"""
    return render_template('register.html', registration_form=RegistrationForm())

@app.route('/post/<int:id>/<slug>')
@login_required
def post(id, slug):
    """Post page"""
    return 'Post page'
