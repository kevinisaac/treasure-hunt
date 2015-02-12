from flask.ext.bcrypt import generate_password_hash
from models import *

# Delete all tables
print 'Deleting tables...'
try:
    db.drop_tables([Submission, Comment, Post, User])
except OperationalError:
    pass
except Exception:
    pass
print 'Done!'

# Create all tables
print 'Creating tables...'
db.create_tables([User, Post, Comment, Submission])
print 'Done!'

# Populate tables
# Add moderators
print 'Poplulating mods...'
mods = ('The Mailman', 'The anonymous phone call', 'Dream', 'Anonymous')
emails = ('rinaldorex94@gmail.com', 'kevin.isaac70@gmail.com', 'nicholasrdavid@gmail.com', 'glenpadua01@gmail.com')
for user, email in zip(mods, emails):
    User.create(name=user, email=email, password=generate_password_hash(email), user_type='mod', token='', college='', register_no='', city='', phone='')
print 'Done!'

# Add users
print 'Poplulating users...'
users = ['apple', 'ball', 'cat', 'dog', 'elephant', 'flower', 'giant', 'hippopotamus', 'idiot', 'janet', 'killer', 'lordkiller', 'mario']
users = []
for user in users:
    User.create(name=user, email=user+'@gmail.com', password=generate_password_hash(user), token='', college='', register_no='', city='', phone='', user_type='')
print 'Done!'
