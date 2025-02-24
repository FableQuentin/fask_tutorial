# Login form
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

# login class, inherits from FlaskForm base class
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    pwd = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')