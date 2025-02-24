# Home page route
# Handles the different URLs that the application supports
# -> in Flask handlers for application routes are written as
#    Python functions called 'view functions'
# -> View functions are mapped to one (or more) URLs
# -> i.e Flask knows what to execute when the client request a given URL  

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit

from app import app, db
from app.forms import LoginForm
from app.models import User

import sqlalchemy as sqla

# ========== INDEX ===========
# We use decorators to create an association between the URL given as argument and the function
# When a browser requests either of the two URL '/' or '/index', Flask is goinf to invoke this function
# and pass its value back to the browser
@app.route('/')
@app.route('/index')
@login_required # redirection to the login page if the user try to access this view function
def index():
	# 'mock' object: we don't have user yet
	user = {'username': 'Bob'}

	# list of posts for my blog
	posts = [
		{
			'author': {'username': 'Jackie Chan'},
			'body': 'Beautiful day in Caen!'
		},
		{
			'author': {'username': 'Bobby Brown'},
			'body': 'I like trains!'
		},		
	]

	# The operation that converts a template into a HTML page is called 'rendering'
	# It is done in Flask using the 'render_template(<filename.html>, <arg>)' function
	# render_templates invokes Jinja template engine (bundled with Flask)
	# Jinja substitutes {{ ... }} block with corresponding values provided in the <arg> of the function 
	return render_template('index.html', title='Home', user=user, posts=posts)

# ========== LOG IN/OUT ===========
#  - loading the page, the browser sends the GET request to receive the web page form
#  - Pressing the 'Submit' button in the form will send the POST request
@app.route('/login', methods=['GET', 'POST']) # tells Flask this view accepts GET and POST requests
def login():
	# In case the user is already logged in but try to access the login page
	# 'current_user' is a Flask-Login variable that can be used at any time during the handling of a request to obtain the
	# user object that represents the client of that request
	if current_user.is_authenticated:
		return redirect(url_for('index'))

	# Log the user in
	# username is obtained from the form submission and we query the database to find the user ('where()' clause)
	# db.session.scalar() will return the user object or None (db.session.scalar() method executes the database query helper function)
	form = LoginForm()
	if form.validate_on_submit():
		user = db.session.scalar(sqla.select(User).where(User.name == form.username.data))

		if user is None or not user.check_password(form.pwd.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))

		# username and password are OK, we call the login_user() function from Flask-Login
		# This function will register the user as logged in and have the current_user variable to that user for any future page loaded 
		login_user(user, remember=form.remember_me.data)
		
		# get the 'next' query string argument
		# Flask provides a 'request' variable that contains all the information that the client sent with a request,
		# including request.args attribute (expose the content of the query string in a dict format)
		# This can be used with the @login_required decorator (set in routes.py) to add query string in a URL, making redirection to
		# '/login?next=/index' in stead of just '/login'
		#
		# In our case, we redirect when the URL is only 'relative' (not absolute), avoinding an attacker to insert an URL to a malicious site in the 'next' argument 
		# To determine if the URL is absolute or relative, it is parsed with 'urlsplit()' function and checked if the 'netloc' component is set or not.
		next_page = request.args.get('next')
		if not next_page or urlsplit(next_page).netloc != '':
			next_page = url_for('index')
		
		return redirect(next_page)
	
	return render_template('login.html', title='Sign in', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))