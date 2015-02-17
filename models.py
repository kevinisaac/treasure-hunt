from datetime import datetime
from peewee import *

# db = PostgresqlDatabase(
#     'd7qflqsae354vb',
#     user='gxejbqspznnxgx',
#     host='ec2-54-235-99-22.compute-1.amazonaws.com',
#     port=5432,
#     password='PSxE9GEUhEvT9cev4z_h7Ywo7p',
#     autocommit=True,
#     autorollback=True
# )
db = MySQLDatabase(
    'cdb_eval_b15bf53043ed33d',
    host = 'us-mm-demo-dca-01.cleardb.com',
    user = '14590faa1103ba',
    password = '0268a94e'
)
# db = MySQLDatabase(
#     'oth',
#     user = 'oth',
#     password = 'oth'
#)

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

class Submission(BaseModel):
    """This model represents a solution submitted by the user."""
    id_post = ForeignKeyField(Post, related_name='post')
    id_user_posted_by = ForeignKeyField(User, related_name='submitted_by_user')
    solution = TextField()
    status = TextField() # accepted, rejected

class Team(BaseModel):
    """This model represents a team."""
    name = TextField()
    id_user_created_by = ForeignKeyField(User, related_name='team_created_by_user')

class TeamUser(BaseModel):
    """This model represents a user with a team."""
    id_team = ForeignKeyField(Team, related_name='team')
    id_user = ForeignKeyField(User, related_name='team_member')
    status = TextField()
