from flask import Flask

app = Flask(__name__)

# Routes
@app.route('/')
def index():
    """Home page"""
    return 'Hello there..'

@app.route('/login')
def login():
    """Login page"""
    return 'Login page'

@app.route('/register')
def register():
    """Registration page"""
    return 'Registration page'

@app.route('/post/<int:id>/<slug>')
def post(id, slug):
    """Post page"""
    return 'Post page'

# Run the app
app.run(debug=True)
