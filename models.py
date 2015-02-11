from datetime import datetime
from peewee import *

db = SqliteDatabase('oth.db')
# db = MySQLDatabase(
#     'cdb_eval_b15bf53043ed33d',
#     host = 'us-mm-demo-dca-01.cleardb.com',
#     user = '14590faa1103ba',
#     password = '0268a94e'
# )

class BaseModel(Model):
    """This is the base model which is inherited by all other models."""
    created_at = DateTimeField(default=datetime.now)

    class Meta(object):
        database = db

class User(BaseModel):
    """This model represents a user in the `user` table."""
    name = CharField()
    email = CharField()
    password = CharField()
    token = CharField()
    user_type = CharField() # participant, admin
    college = CharField()
    city = CharField()
    register_no = CharField()
    phone = CharField()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

class Post(BaseModel):
    """This model represents a post."""
    correct_solution = TextField()
    title = CharField()
    description = TextField()
    id_user_posted_by = ForeignKeyField(User, related_name='post_posted_by_user')
    level = IntegerField()
    points = IntegerField()
    problem_type = CharField() # regular, bonus

class Comment(BaseModel):
    """This model represents a comment to a post."""
    description = TextField()
    id_post_belongs_to = ForeignKeyField(Post, related_name='belongs_to_post')
    id_user_posted_by = ForeignKeyField(User, related_name='comment_posted_by_user')
    status = CharField() # accepted, rejected

class Problem(BaseModel):
    """This model represents a problem."""
    description = TextField()
    id_user_posted_by = ForeignKeyField(User, related_name='problem_posted_by_user')

class Submission(BaseModel):
    """This model represents a solution submitted by the user."""
    id_post = ForeignKeyField(Post, related_name='post')
    id_user_posted_by = ForeignKeyField(User, related_name='submitted_by_user')
    solution = TextField()
    status = TextField() # accepted, rejected
