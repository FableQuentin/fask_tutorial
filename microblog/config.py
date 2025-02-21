# configuration variables
import os

# A configuration class is used to store config variables
# Config settings are defined as class variables 
# 'SECRET_KEY' is a configuration variable (here obtained from 'SECRET_KEY' environment variable) 
# Flask (and extensions) uses it to protect web form against CSRF (Cross-Site Request Forgery): 
# submission of unauthorized web requests/commands submitted form trusted user
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'