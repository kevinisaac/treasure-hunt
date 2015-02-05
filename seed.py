from flask.ext.bcrypt import generate_password_hash
from models import *

# Delete all tables
print 'Deleting tables...'
try:
    db.drop_tables([Submission, Comment, Post, User])
except OperationalError:
    pass
print 'Done!'

# Create all tables
print 'Creating tables...'
db.create_tables([User, Post, Comment, Submission])
print 'Done!'

# Populate tables
# Add moderators
print 'Poplulating mods...'
mods = ['rex', 'kevin', 'nicholas']
for user in mods:
    User.create(name=user, email=user+'@gmail.com', password=generate_password_hash(user), user_type='mod')
print 'Done!'

# Add users
print 'Poplulating users...'
users = ['apple', 'ball', 'cat', 'dog', 'elephant', 'flower', 'giant', 'hippopotamus', 'idiot', 'janet', 'killer', 'lordkiller', 'mario']
for user in users:
    User.create(name=user, email=user+'@gmail.com', password=generate_password_hash(user))
print 'Done!'
