from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

#__name__ is Python predefined variable which is set to the name of the module in which it is used
# Flask uses the location of the module passed here as a starting point when it needs to load associated resources such as template files
# The app variable is defined as an instance of class Flask in the __init__.py script, which makes it a member of the app package.
app = Flask(__name__)

# Tell Flask to read the config file and apply it
app.config.from_object(Config)

# Database instance
db = SQLAlchemy(app)
# Database migration engine instance
migrate = Migrate(app, db)

# Flask-Login instance
login = LoginManager(app)
login.login_view = 'login' # define the default login view

# Flask logger object (send logs by email)
if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR) # only ERROR level errors (not WARNING, INFO or DEBUG)
        app.logger.addHandler(mail_handler)    

# Log files handler
if not app.debug:
    # create logs folder
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # RotatingFileHandler: rotates the logs, ensuring that the log files do not grow too large when the application runs for a long time. 
    # Here:
    #  -> limit size of the log file to 10KB
    #  -> keep the last ten log files as backup
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    # ->  custom formatting for the log message
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    # -> categories are (oreder of severity): DEBUG, INFO, WARNING, ERROR and CRITICAL
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    # First line in log: start/restart of the application
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

# Flask-Email instance
mail = Mail(app)


# ==========================================
# The bottom import is a well known workaround that avoids circular imports, a common problem with Flask applications. 
# routes module needs to import the app variable defined in this script, so putting one of the reciprocal imports at the bottom 
# avoids the error that results from the mutual references between these two files.
#
# The routes handle the different URLs that the application supports. 
# In Flask, handlers for the application routes are written as Python functions, called view functions. 
# View functions are mapped to one or more route URLs so that Flask knows what logic 
# to execute when a client requests a given URL.
from app import routes

# Module used to define the structure of database
from app import models

# Module used for error handling
from app import errors