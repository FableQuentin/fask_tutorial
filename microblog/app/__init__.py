from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

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