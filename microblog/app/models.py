from datetime import datetime, timezone
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash

import sqlalchemy as sqla # provides general purpose database functions and classes
import sqlalchemy.orm as sqlo # provides support for using models
import jwt

from app import app, db, login
from flask_login import UserMixin
from hashlib import md5
from time import time


# Followers association table
# Notes:
# -> this table is declared above the model(s) that uses it (User in our case);
# -> this table is not declared as a model: this is an auxiliary table that has no data other than the foreign keys (no associated model class needed).
followers = sqla.Table(
    'followers',
    db.metadata, # metadata instance: is the place where SQLAlchemy stores all info about all tables in the database
    sqla.Column('follower_id', sqla.Integer, sqla.ForeignKey('user.id'), primary_key=True),
    sqla.Column('followed_id', sqla.Integer, sqla.ForeignKey('user.id'), primary_key=True)
)

# Class to store users in the database
# Inherits from db.Model, a base class for all Flask-SQLAlchemy models
# sqlo.Mapped[int] defines a type of column which is not nullable (can't be empty)
# sqlo.Mapped[Optional[str]] defines a type of column that can be empty (Optional) 
# In most cases defining a table column requires more than the column type. 
# SQLAlchemy uses a so.mapped_column() function call assigned to each column to provide this additional configuration.
# -> index:  indicate which fields are indexed (can be retrieved)
# -> unique: indicate which fields are unique
# -> Important so that database is consistent and searches are efficient
class User(UserMixin, db.Model):
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    username: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), index=True, unique=True)
    email: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(120), index=True, unique=True)
    pwd_hash: sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(256))

    # user info 
    about_me: sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(140))
    last_seen: sqlo.Mapped[Optional[datetime]] = sqlo.mapped_column(default=lambda: datetime.now(timezone.utc))
    
    # Users' posts field: references values from the id column in the users table
    # WriteOnlyMapped defines posts as a collection type with 'Post' objects inside.
    # This is not an actual database field, but a high-level view of the relationship between users and posts
    posts: sqlo.WriteOnlyMapped['Post'] = sqlo.relationship(back_populates='author')

    # following/followers
    # Link User instances to other User instances: UserA and UserB
    # Here are the sqlo.relationship() arguments:
    # - secondary:  configures the association table that is used for this relationship (followers, defined above)
    # - primaryjoin: indicates the condition that links the entity to the association table.
    #                In the 'following' relationship, the user has to match the 'follower_id' attribute of the association table.
    #                (In the 'followers' relationship, the roles are reversed)
    #                The 'followers.c.follower_id' expression references the 'follower_id' column of the association table
    # - secondaryjoin: indicates the condition that links the association table to the user on the other side of the relationship.
    #                  In the 'following' relationship, the user has to match the 'followed_id' column
    #                  In the 'followers' relationship, the user has to match the 'follower_id' column.
    #

    # UserA point of view for query (left-side): get the list of users the UserA is following 
    following: sqlo.WriteOnlyMapped['User'] = sqlo.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id), secondaryjoin=(followers.c.followed_id == id), back_populates='followers'
    )
    # UserB point of view for query (right-side): get the list of users that follows UserA
    followers: sqlo.WriteOnlyMapped['User'] = sqlo.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id), secondaryjoin=(followers.c.follower_id == id), back_populates='following'
    ) 

    # Password hashing
    def set_password(self, pwd):
        self.pwd_hash = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.pwd_hash, pwd)
    
    # User avatar URLs (for Gravatar)
    def get_avatar_url(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    # Add/remove followers
    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    # sqla.func.count() function from SQLAlchemy, indicate that I want to get the result of a function. 
    # The select_from() clause is then added with the query that needs to be counted. 
    # Whenever a query is included as part of a larger query, SQLAlchemy requires the inner query to be converted 
    # to a sub-query by calling the subquery() method.
    def followers_count(self):
        query = sqla.select(sqla.func.count()).select_from(self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self):
        query = sqla.select(sqla.func.count()).select_from(self.following.select().subquery())
        return db.session.scalar(query)               
    
    # Following post query: obtain the post from followed users only
    # sqla.select('Post'): select the entity that needs to be obtained (here 'Post')
    # <left>.join(<right>): 
    # -> join query from <left> and <right> sides of the relationship (combine rows from two tables according to given criteria)
    # -> the combined table is a temporary table that can be used only during the query
    # ex: sqla.select(Post).join(Post.author): select 'Post' entities joined to Post.author: 
    # this creates an extended table that provide access to posts along with author of each post  
    #
    # .of_type('Author'): tells SQLAlchemy that in the rest of the query I'm going to refer to the right side entity of the relationship with the Author alias.
    # .group_by(): eliminate any duplicate of the provided arguments
    # .order_by(): results sorted by the timestamp field of the post in descending order
    def following_posts(self):
        # create aliases
        Author = sqlo.aliased(User)
        Follower = sqlo.aliased(User)
        return (
            sqla.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sqla.or_(Follower.id == self.id, Author.id == self.id))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )     

    # Reset password token methods
    def get_reset_password_token(self, expires_in=600):
        # JSON web token
        return jwt.encode(
        {'reset_password': self.id, 'exp': time() + expires_in},
        app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_reset_password_token(token):
        # if the token is valid, then the value of the 'reset_password' key from the token's payload 
        # is the ID of the user, so I can load the user and return it
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        
        except:
            return
        
        return db.session.get(User, id)    

    # __repr__: method telling Python how to print objects of this class
    def __repr__(self):
        return '<User {}>'.format(self.username)

# User loader function
# As Flask-Login knows nothing about databases, it needs the application's help in loading a user. 
# For that reason, the extension expects that the application will configure a user loader function, that can be called to load a user given the ID.
# The ID is passed to the function by Flask-Login as a string (converted into integer as the database uses numeric IDs)
#
# Note: 
# - db.session is the database session manager, it allows you to interact with the database (transactions, queries and updates to your database)
# - db.session.scalar(): use to fetch single a single scalar value (like id, email, etc...) to avoid unnecessary data 
# - db.session.scalars(): use to fetch mutiple values
# - db.select(): in SQLAlchemy 2.0, queries are constructed with db.select() (creates a SELECT statement)
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

# Class to store posts in the database
class Post(db.Model):
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    body: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(140))
    timestamp: sqlo.Mapped[datetime] = sqlo.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(User.id), index=True)

    # Other side of the relationship between users and posts
    author: sqlo.Mapped[User] = sqlo.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
