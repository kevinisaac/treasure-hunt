from flask import (
    abort,
    flash,
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from flask.ext.bcrypt import generate_password_hash, check_password_hash
from flask.ext.login import (
    current_user,
    LoginManager,
    login_required,
    login_user,
    logout_user
)
from forms import (
    CommentForm,
    LoginForm,
    PostForm,
    RegistrationForm,
    SubmissionForm
)
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
    try:
        max_post = (Post.select()
                .join(Submission)
                .where(Submission.id_user_posted_by == int(current_user.id))
                .where(Submission.status == 'accepted')
                .order_by(Post.level.desc())
                .get()
                )
        level = max_post.level + 1
    except DoesNotExist:
        level = 1
    posts = Post.select().where(Post.level <= level)
    return render_template('posts.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
# @logout_required('.index')
def login():
    """Login page"""
    print
    print dir(session)
    print
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

@app.route('/register', methods=['GET', 'POST'])
# @logout_required('index')
def register():
    """Registration page"""
    print current_user.is_authenticated()
    if request.method == 'GET':
        return render_template('register.html', registration_form=RegistrationForm())
    else:
        registration_form = RegistrationForm(request.form)
        if registration_form.validate():
            new_user = User.create(
                name=request.form['name'],
                email=request.form['email'],
                password=generate_password_hash(request.form['password'])
            )
            login_user(new_user)
            flash('Account created successfully!')
            return redirect(url_for('index'))
        return render_template('register.html', registration_form=RegistrationForm())

@app.route('/posts/<int:id>/<slug>', methods=['GET', 'POST'])
@login_required
def post(id, slug):
    """Post page"""
    try:
        post = Post.get(id=id)
    except DoesNotExist:
        abort(404)
    if request.method == 'POST':
        if not request.args.get('solution'):
            comment_form = CommentForm(request.form)
            if comment_form.validate():
                # Update the database - add the comment
                Comment.create(
                    description=comment_form.description.data,
                    id_post_belongs_to=int(id),
                    id_user_posted_by=int(current_user.id)
                )
                return redirect(url_for('post', id=id, slug=slug))
        else:
            submission_form = SubmissionForm(request.form)
            try:
                accepted_submission = Submission.get(
                    Submission.id_user_posted_by==int(current_user.id),
                    Submission.id_post==int(id),
                    Submission.status=='accepted'
                )
            except DoesNotExist:
                accepted_submission = None
            if submission_form.validate() and accepted_submission is None:
                status = 'rejected'
                if str(submission_form.solution.data) == str(Post.get(id=int(id)).correct_solution):
                    status = 'accepted'
                Submission.create(
                    id_post=int(id),
                    id_user_posted_by=int(current_user.id),
                    solution=submission_form.solution.data,
                    status=status
                )
            else:
                flash('Already submitted correct answer')
    if post is not None:
        try:
            comments = Comment.select().where(Comment.id_post_belongs_to==post.id)
        except DoesNotExist:
            pass
    return render_template('post.html', post=post, comments=comments, comment_form=CommentForm(), submission_form=SubmissionForm())

@app.route('/posts/<int:id>/<slug>/delete', methods=['POST'])
@login_required
def delete_post(id, slug):
    if current_user.user_type == 'mod':
        print '--------------------------------------------------------------'
        print 'deleting', id
        post = Post.get(Post.id == int(id))
        post.delete_instance()
        return ''

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    return 'Account'

@app.route('/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def profile(id):
    """Profile of a user."""
    user = User.get(id=id)
    return render_template('profile.html', user=user)

@app.route('/posts/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Place where a user creates a post."""
    if request.method == 'GET':
        return render_template('create_post.html', post_form=PostForm())
    elif request.method == 'POST':
        post_form = PostForm(request.form)
        print 'df'
        if post_form.validate():
            correct_solution = ''
            level = 0
            points = 0
            problem_type = ''
            if 'problem_type' in request.form:
                correct_solution = request.form['correct_solution']
                level = request.form['level']
                points = request.form['points']
                problem_type = request.form['problem_type']
            Post.create(
                description=request.form['description'],
                id_user_posted_by=int(current_user.id),
                title=request.form['title'],
                correct_solution=correct_solution,
                level=level,
                points=points,
                problem_type=problem_type
            )
            return 'Post created.'
        return render_template('create_post.html', post_form=PostForm())
