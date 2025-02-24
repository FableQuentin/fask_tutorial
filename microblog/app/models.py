from datetime import datetime, timezone
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sqla # provides general purpose database functions and classes
import sqlalchemy.orm as sqlo # provides support for using models
from app import db, login
from flask_login import UserMixin

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
    
    # Users' posts field: references values from the id column in the users table
    # WriteOnlyMapped defines posts as a collection type with Post objects inside.
    # This is not an actual database field, but a high-level view of the relationship between users and posts
    posts: sqlo.WriteOnlyMapped['Post'] = sqlo.relationship(back_populates='author')

    # Password hashing
    def set_password(self, pwd):
        self.pwd_hash = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.pwd_hash, pwd)

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
