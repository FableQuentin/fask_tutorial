# configuration variables
import os

# Store the main directory of the application in a variable
basedir = os.path.abspath(os.path.dirname(__file__))

# A configuration class is used to store config variables
# Config settings are defined as class variables 
class Config:
    # 'SECRET_KEY' is a configuration variable (here obtained from 'SECRET_KEY' environment variable) 
    # Flask (and extensions) uses it to protect web form against CSRF (Cross-Site Request Forgery): 
    # submission of unauthorized web requests/commands submitted form trusted user
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'    
    
    # Flask-SQLAlchemy configuration
    # 'SQLALCHEMY_DATABASE_URI' is a configuration variable obtained from 'DATABASE_URL' environment variable
    # If not defined, we configure a database named app.db located in the main directory of the application  (stored in the basedir variable)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')

    # Email server configuration (for error handlers)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25) #default port is 25
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['quentin.fable@gmail.com'] #list of email addresses that will receive error reports

    # Number of Posts per pagination
    POSTS_PER_PAGE = 5