from peewee import *

db = MySQLDatabase('oth', user='oth', password='oth')

class BaseModel(Model):
    """This is the base model which is inherited by all other models."""
    created_at = DateTimeField()

    class Meta(object):
        database = db 

class User(BaseModel):
    """This model represents a user in the `user` table."""
    name = CharField()
    email = CharField()
    password = CharField()
    token = CharField()
    user_type = CharField() # participant, admin

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
    title = CharField()
    description = TextField()
    id_user_posted_by = ForeignKeyField(User, related_name='post_posted_by_user')

class Comment(BaseModel):
    """This model represents a comment to a post."""
    description = TextField()
    id_post_belongs_to = ForeignKeyField(Post, related_name='belongs_to_post')
    id_user_posted_by = ForeignKeyField(User, related_name='comment_posted_by_user')

class Problem(BaseModel):
    """This model represents a problem."""
    correct_solution = TextField()
    description = TextField()
    id_user_posted_by = ForeignKeyField(User, related_name='problem_posted_by_user')
    level = IntegerField()
    points = IntegerField()
    problem_type = CharField() # regular, bonus

class Submission(BaseModel):
    """This model represents a solution submitted by the user."""
    id_problem = ForeignKeyField(Problem, related_name='problem')
    id_user_posted_by = ForeignKeyField(User, related_name='submitted_by_user')
    solution = TextField()
    status = TextField() # accepted, rejected
