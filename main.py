import hashlib, operator, os
from flask import (
    abort,
    flash,
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message
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
    PasswordForm,
    PostForm,
    ProfileForm,
    RegistrationForm,
    SubmissionForm,
    UploadForm
)
from models import *
from slugify import slugify
from werkzeug import secure_filename

from core import logout_required

# app = Flask(__name__, instance_relative_config=True)
app = Flask(__name__)

# Load the default config
print 'before app creation'
app.config.from_object('config')
# app.config.from_pyfile('config.py')
print 'app created'

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# toolbar = DebugToolbarExtension(app)
mail = Mail(app)
print 'mail instantiated'

def get_all_users():
    try:
        users = User.select().where(User.user_type!='mod', User.token=='')
    except DoesNotExist:
        return []
    data = []
    rank = 1
    for user in users:
        # Get the level of the user
        try:
            max_post = (Post.select()
                .where(Post.problem_type != 'bonus')
                .join(Submission)
                .where(Submission.id_user_posted_by == int(user.id))
                .where(Submission.status == 'accepted')
                .order_by(Post.level.desc())
                .get()
            )
            level = max_post.level + 1
        except DoesNotExist:
            level = 1
        user.level = level
        print 'gau - level got'
        
        # Get the total points of the user
        points = 0
        try:
            posts = (
                Post.select(Post.points)
                .join(Submission)
                .where(Submission.id_user_posted_by==int(user.id))
                .where(Submission.status=='accepted')
            )
            for post in posts:
                points += post.points
        except DoesNotExist:
            pass
        user.points = points
        print 'gau - points got'
        data.append({
            'id': user.id,
            'profile_link': user.name,
            'name': '<a target="_blank" href="/profile/' + str(user.id) + '">' + user.name + '</a>',
            'college': user.college,
            'city': user.city,
            'level': user.level,
            'points': user.points
        })
    users = sorted(data, key=operator.itemgetter('points'), reverse=True)
    print 'gau - sorted'
    for user in users:
        print user['name']
        user['rank'] = rank
        rank += 1
    return data

@login_manager.user_loader
def load_user(userid):
    return User.get(id=int(userid))

# Before and after
@app.before_request
def before_request():
    print 'before connect'
    db.connect()
    print 'after connect'

@app.teardown_request
def teardown_request(exception):
    db.close()

# Routes
@app.route('/test/mail')
@login_required
def test_mail():
    msg = Message(
        "Welcome to Online Treasure Hunt",
        recipients = ['mindkraft.treasure.hunt@gmail.com']
    )
    msg.body = """
    Hello. Thanks for signing up. Click on the following link to activate your account.

    https://online-treasure.herokuapp.com/verify?token=

    See you on the other side!
    """
    mail.send(msg)

@app.route('/')
@login_required
def index():
    """Home page"""
    print current_user.is_authenticated()
    # Get the level of the user
    try:
        max_post = (Post.select()
            .where(Post.problem_type != 'bonus')
            .join(Submission)
            .where(Submission.id_user_posted_by == int(current_user.id))
            .where(Submission.status == 'accepted')
            .order_by(Post.level.desc())
            .get()
        )
        level = max_post.level + 1
    except DoesNotExist:
        level = 1
    print 'level of user got'
    
    if current_user.user_type == 'mod':
        posts = Post.select().order_by(Post.id.desc())
    else:
        posts = Post.select().where(Post.level <= level).order_by(Post.id.desc())
    print 'posts got'
    
    # Get the status of the post
    for post in posts:
        try:
            submission = Submission.get(
                Submission.id_post==post.id,
                Submission.id_user_posted_by==int(current_user.id),
                Submission.status=='accepted'
            )
            post.status = 'Solved'
        except DoesNotExist:
            post.status = 'Unsolved'
        
        # If post is normal type, no need of status
        if post.problem_type == '':
            post.status = ''
        
        # Get the name of person who posted this
        user = (
            User.select(User.name)
            .join(Post)
            .where(Post.id == post.id)
            .get()
        )
        post.posted_by = user.name
        
        # Add slug title to the post
        post.slug = slugify(post.title)
    print 'posts status got'
    
    return render_template('posts.html', posts=posts, top_users=get_all_users())

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.user_type != 'mod':
        abort(404)
    if request.method == 'GET':
        return render_template('upload.html', upload_form=UploadForm(), top_users=get_all_users())
    else:
        file = request.files['image']
        filename = secure_filename(file.filename)
        print
        print os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect('/static/img/' + filename)

@app.route('/login', methods=['GET', 'POST'])
# @logout_required('.index')
def login():
    """Login page"""
    logout_user()
    if request.method == 'GET':
        return render_template('login.html', login_form=LoginForm(), top_users=get_all_users())
    else:
        login_form = LoginForm(request.form)
        if login_form.validate_on_submit():
            email = request.form.get('email')
            login_user(User.get(User.email==email))
            return redirect(request.args.get('next') or url_for('index'))
        return render_template('login.html', login_form=LoginForm(), top_users=get_all_users())

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
    logout_user()
    if request.method == 'GET':
        return render_template('register.html', registration_form=RegistrationForm(), top_users=get_all_users())
    registration_form = RegistrationForm(request.form)
    if registration_form.validate():
        token = hashlib.md5(
            request.form['name'] + '+=' + request.form['email']
        ).hexdigest()
        new_user = User.create(
            city=request.form['city'],
            college=request.form['college'],
            email=request.form['email'],
            name=request.form['name'],
            password=generate_password_hash(request.form['password']),
            phone=request.form['phone'],
            register_no=request.form['register_no'],
            token=token
        )
        # Send confirmation email
        recipients = ['mindkraft.treasure.hunt@gmail.com', new_user.email]
        for recipient in recipients:
            msg = Message(
                "Welcome to Online Treasure Hunt - Mindkraft 2015",
                recipients = [recipient]
            )
            msg.body = """
            Hello. Thanks for signing up. Click on the following link to activate your account.
            
            https://online-treasure.herokuapp.com/account/validate?email=%s&token=%s
            
            See you on the other side!
            """ % (new_user.email, new_user.token)
            try:
                mail.send(msg)
            except Exception:
                flash('Login to continue')
                return redirect('https://online-treasure.herokuapp.com/account/validate?email=' + str(new_user.email) + '&token=' + str(new_user.token))
        flash('Account created successfully! Head over to ' + request.form['email'] + ' for confirmation link.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', registration_form=RegistrationForm(), top_users=get_all_users())

@app.route('/posts/<int:id>/<slug>', methods=['GET', 'POST'])
@login_required
def post(id, slug):
    """Post page"""
    try:
        # Get the level of the user
        try:
            max_post = (Post.select()
                .where(Post.problem_type != 'bonus')
                .join(Submission)
                .where(Submission.id_user_posted_by == int(current_user.id))
                .where(Submission.status == 'accepted')
                .order_by(Post.level.desc())
                .get()
            )
            level = max_post.level + 1
        except DoesNotExist:
            level = 1
        
        # post = Post.select().where(Post.level <= level).order_by(Post.id.desc())
        if current_user.user_type == 'mod':
            post = Post.get(Post.id == id)
        else:
            post = Post.get(Post.id == id, Post.level <= level)
        # post = Post.get(id=id)
    except DoesNotExist:
        abort(404)
    
    # Get the status of the post
    try:
        submission = Submission.get(
            Submission.id_post==post.id,
            Submission.id_user_posted_by==int(current_user.id),
            Submission.status=='accepted'
        )
        post.status = 'Solved'
    except DoesNotExist:
        post.status = 'Unsolved'
    
    # If post is normal type, no need of status
    if post.problem_type == '':
        post.status = ''

    # Get the name of person who posted this
    user = (
        User.select(User.name)
        .join(Post)
        .where(Post.id == post.id)
        .get()
    )
    post.posted_by = user.name

    # Get the users who have solved this puzzle
    solved_by_users_obj = (
        User.select(User.name, User.id)
        .join(Submission)
        .where(Submission.status == 'solved')
        .where(Submission.id_post == id)
    )
    solved_by_users = []
    for user in solved_by_users_obj:
        print
        print user.name, user.id
        print
        solved_by_users.append({
            'name': user.name,
            'id': user.id
        })
    
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
                flash('Your comment is waiting moderator approval')
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
                if str(submission_form.solution.data).lower().strip() == str(Post.get(id=int(id)).correct_solution).lower().strip():
                    status = 'accepted'
                    flash('Your answer was correct. Congratulations!')
                else:
                    flash('Incorrect answer')
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
            comments = (Comment
                .select()
                .join(User)
                .where(
                Comment.id_post_belongs_to==post.id,
                (Comment.status == '') | (Comment.status == 'accepted')
            )
        )
        except DoesNotExist:
            pass
        for comment in comments:
            print dir(comment)
    return render_template(
        'post.html',
        post=post,
        comments=comments,
        comment_form=CommentForm(),
        submission_form=SubmissionForm(),
        solved_by_users=solved_by_users,
        top_users=get_all_users()
    )

@app.route('/posts/<int:id>/<slug>/delete', methods=['POST'])
@login_required
def delete_post(id, slug):
    if current_user.user_type != 'mod':
        abort(404)
    if current_user.user_type == 'mod':
        # Delete all comments
        comments = (
            Comment
            .select()
            .where(Comment.id_post_belongs_to == id)
        )
        for comment in comments:
            comment.delete_instance()
        
        # Delete the post
        post = Post.get(Post.id == int(id))
        post.delete_instance()
        
        flash('Post deleted successfully')
        return redirect(url_for('index'))

@app.route('/comments/<int:id>/accept')
def accept_comment(id):
    if current_user.user_type != 'mod':
        return 'No permission'
    comment = Comment.get(id=id)
    comment.status = 'accepted'
    comment.save()
    return redirect(url_for('index'))

@app.route('/comments/<int:id>/reject')
def reject_comment(id):
    if current_user.user_type != 'mod':
        return 'No permission'
    comment = Comment.get(id=id)
    comment.status = 'rejected'
    comment.save()
    return redirect(url_for('index'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'GET':
        return render_template('account.html', profile_form=ProfileForm(), password_form=PasswordForm(), top_users=get_all_users())
    else:
        # Update profile details
        profile_form = ProfileForm(request.form)
        if profile_form.validate():
            user = User.get(id=int(current_user.id))
            user.name = profile_form.name.data
            user.college = profile_form.college.data
            user.city = profile_form.city.data
            user.register_no = profile_form.register_no.data
            user.phone = profile_form.phone.data
            user.save()
            return redirect(url_for('account'))
        return 'Invalid form'

@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    password_form = PasswordForm(request.form)
    if password_form.validate():
        user = User.get(id=int(current_user.id))
        user.password = generate_password_hash(password_form.password.data)
        user.save()
        print 'gone'
        flash('Password changed successfully!')
        return redirect(url_for('account'))
    flash('Password cannot be updated. Do the passwords match?')
    return redirect(url_for('account'))

@app.route('/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def profile(id):
    """Profile of a user."""
    user = User.get(id=id)
    
    # Get the level of the user
    try:
        max_post = (Post.select()
            .where(Post.problem_type != 'bonus')
            .join(Submission)
            .where(Submission.id_user_posted_by == int(user.id))
            .where(Submission.status == 'accepted')
            .order_by(Post.level.desc())
            .get()
        )
        level = max_post.level + 1
    except DoesNotExist:
        level = 1
    user.level = level
    
    # Get the rank of the user
    for u in get_all_users():
        if u['id'] == user.id:
            user.rank = u['rank']
            break
    
    # Get the total points of the user
    points = 0
    try:
        posts = (
            Post.select(Post.points)
            .join(Submission)
            .where(Submission.id_user_posted_by==int(user.id))
            .where(Submission.status=='accepted')
        )
        for post in posts:
            points += post.points
    except DoesNotExist:
        pass
        
    user.level = level
    user.points = points
    
    return render_template('profile.html', user=user, top_users=get_all_users())

@app.route('/posts/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Place where a user creates a post."""
    if current_user.user_type != 'mod':
        abort(404)
    if request.method == 'GET':
        return render_template('create_post.html', post_form=PostForm(), top_users=get_all_users())
    elif request.method == 'POST':
        post_form = PostForm(request.form)
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
            return redirect(url_for('index'))
        return render_template('create_post.html', post_form=PostForm(), top_users=get_all_users())

@app.route('/posts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post():
    """Edit the details of a post."""
    if current_user.user_type != 'mod':
        abort(404)
    if request.method == 'GET':
        return render_template('edit_post.html', post_edit_form=PostEditForm(), top_users=get_all_users())
    else:
        pass


# Leaderboard

# Template
@app.route('/leaderboard')
def leaderboard():
    users_list = get_all_users()
    return render_template('leaderboard.html', top_users=users_list)

# API
@app.route('/api/leaderboard')
def leaderboard_api():
    users_list = get_all_users() # Returns a list of users
    return jsonify(data=users_list)

# Mail related routes
# Validate account route
@app.route('/account/validate')
def validate_account():
    logout_user()
    
    if not request.args.get('email') or not request.args.get('token'):
        abort(404)
    
    # Abort if no user is found
    try:
        user = User.get(User.email==request.args.get('email'))
    except DoesNotExist:
        abort(404)
    
    # Check if account is already verified
    if user.token == '':
        flash('Account already verified')
        return redirect(url_for('login'))
    
    #  Check if invalid token
    if user.token != request.args.get('token'):
        return 'Invalid token'
    
    # Verify account
    user.token = ''
    user.save()
    
    # Send welcome email
    recipients = ['mindkraft.treasure.hunt@gmail.com', user.email]
    for recipient in recipients:
        msg = Message(
            "Welcome to Online Treasure Hunt",
            recipients = [recipient]
        )
        msg.html = """
        Hey %s!<br /><br />
        
        We're glad that you're interested in this quest! This is an online treasure hunt type event. Like all other such events, this consists of a series of puzzles that you'll solve consecutively to move on to the next level until you find this final "Treasure".<br /><br />
        
        Trust us; you'll have a good deal of fun playing this! This event is packed with tons of bonus puzzles, riddles, fun and prizes for the top detective(s).<br /><br />
        
        <b>What do I have to do?</b><br /><br />
        
        Nothing. You've already registered. We'll help you get started. Follow the simple steps.<br />
        
        &nbsp&nbsp&nbsp1. Head over to online-treasure.herokuapp.com.<br />
        &nbsp&nbsp&nbsp2. Login with your username/mail and password.<br />
        &nbsp&nbsp&nbsp3. Head over to the home page (By clicking on the "Online treasure hunt" page title).<br />
        &nbsp&nbsp&nbsp4. You'll see a list of posts. Go through them. Read them carefully. They'll guide you from there.<br />
        &nbsp&nbsp&nbsp5. Have fun.<br />

        <b>How do I contact you in case of any queries?</b><br /><br />
        
        In case of queries regarding puzzles, comment it out. In case of general queries and discussions, visit our sub-reddit : <a href="https://reddit.com/r/iamsherlocked">/r/iamsherlocked</a>.<br /><br />
        
        <b>I've got more questions. Is there an FAQ?</b><br /><br />
        
        Come on now! It's not that tough. Just start up already, you'll catch up! ;)<br /><br />
        
        Regards,<br />
        The SherLOCKED team.<br /><br />
        
        Find us at:<br />
            <a href="https://online-treasure.herokuapp.com">221b Baker Street</a><br />
            Forum - <a href="https://reddit.com/r/iamsherlocked">/r/iamsherlocked</a>
        """ % (recipient)
        try:
            mail.send(msg)
        except Exception:
            pass
    
    flash('Account verified successfully! Login to continue')
    return redirect(url_for('login'))

# Email my password reset link
@app.route('/account/reset', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        # Abort if no user is found
        try:
            user = User.get(User.email==request.args.get('email'))
        except DoesNotExist:
            abort(404)
    
        password_form = PasswordForm(request.form)
        if password_form.validate():
            user = User.get(id=int(user.id))
            user.password = generate_password_hash(password_form.password.data)
            user.save()
            flash('Password changed successfully! Login to your account now')
            return redirect(url_for('login'))
        flash('Password cannot be updated. Do the passwords match?')
        return redirect(url_for('reset_password'))

    
    if not request.args.get('email') or not request.args.get('token'):
        abort(404)
    
    # Abort if no user is found
    try:
        user = User.get(User.email==request.args.get('email'))
    except DoesNotExist:
        abort(404)
    
    if request.args.get('token') != hashlib.md5(user.password).hexdigest():
        return 'Wrong token. Please try again!'
    
    return render_template('resetpassword.html', password_form=PasswordForm(), top_users=get_all_users())

@app.route('/account/reset/form', methods=['GET', 'POST'])
def reset_password_form():
    logout_user()
    if request.method == 'GET':
        return render_template('forgotpassword.html', top_users=get_all_users())
    try:
        user = User.get(User.email == request.form['email'])
    except DoesNotExist, e:
        flash('No such user registered')
        return redirect(url_for('reset_password_form'))
    #TODO: Send the password to the email
    
    # Send confirmation email
    recipients = [user.email]
    for recipient in recipients:
        msg = Message(
            "Password reset link",
            recipients = [recipient]
        )
        msg.body = """
        Click on the following link to reset your password:
        
        https://online-treasure.herokuapp.com/account/reset?email=%s&token=%s
        
        """ % (user.email, hashlib.md5(user.password).hexdigest())
        mail.send(msg)
    
    print hashlib.md5(user.password).hexdigest()
    flash('Password reset email has been sent')
    return redirect(url_for('reset_password_form'))
