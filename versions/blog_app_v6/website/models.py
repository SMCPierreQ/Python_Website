from. import db 
from flask_login import UserMixin
from sqlalchemy.sql import func 

#Database model for user data
class User(db.Model, UserMixin):
    #User identifier, an integer, unique
    id = db.Column(db.Integer, primary_key=True)
    #User email, has to be unique
    email = db.Column(db.String(150), unique=True)
    #Username, has to be unique
    username = db.Column(db.String(150), unique=True)
    #Password, hashed in database
    password = db.Column(db.String(150))
    #User profile picture
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    #Date and time when account was made
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    #Links User database class to Post database class
    posts = db.relationship('Post', backref='user', passive_deletes=True)
    #Links User database class to Comment database class
    comments= db.relationship('Comment', backref='user', passive_deletes=True)

#Database model for posts from users
class Post(db.Model):
    #Post identifier, an integer, unique
    id = db.Column(db.Integer, primary_key=True)
    #Post title 
    title = db.Column(db.String(100), nullable=False)
    #Post content
    text = db.Column(db.Text, nullable=False)
    #Date and time when post was made
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    #Author of post, finds via user ID.
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    #Links Post database to Comment database class
    comments= db.relationship('Comment', backref='post', passive_deletes=True)

#Database model for comments from users
class Comment(db.Model):
    #Comment identifier, an integer, unique
    id = db.Column(db.Integer, primary_key=True)
    #Comment content
    text = db.Column(db.Text, nullable=False)
    #Date and time when comment was made
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    #Author of comment, finds via user ID.
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    #Post where comment is located, finds via post ID.
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)