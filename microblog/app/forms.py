# Login form
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

import sqlalchemy as sqla
from app import db
from app.models import User

# login class, inherits from FlaskForm base class
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    pwd = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')

# registration form 
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    pwd = PasswordField('Password', validators=[DataRequired()])
    pwd2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('pwd')])
    submit = SubmitField('Register')


    # Note : using validate_<field_name> in a custom form, WTForms takes those functions as custom validators
    # and invokes them in addition to stock validators 
    def validate_username(self, username):
        user = db.session.scalar(sqla.select(User).where(User.username == username.data))

        if user is not None:
            raise ValidationError('Please use another username.')

    def validate_email(self, email):
        user = db.session.scalar(sqla.select(User).where(User.email == email.data))

        if user is not None:
            raise ValidationError('Please use another email address.')

