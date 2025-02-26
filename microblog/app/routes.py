# Home page route
# Handles the different URLs that the application supports
# -> in Flask handlers for application routes are written as
#    Python functions called 'view functions'
# -> View functions are mapped to one (or more) URLs
# -> i.e Flask knows what to execute when the client request a given URL  

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from datetime import datetime, timezone

from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm
from app.models import User, Post

import sqlalchemy as sqla

# ========== INDEX ===========
# We use decorators to create an association between the URL given as argument and the function
# When a browser requests either of the two URL '/' or '/index', Flask is goinf to invoke this function
# and pass its value back to the browser
@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
@login_required # redirection to the login page if the user try to access this view function
def index():
	# add post submission form in index view function
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body=form.post.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post is now live!')

		# redirect to index page: if a 'POST' request is answered with a redirect, 
		# the browser is instructed to send a 'GET' request to grab the page indicated in the redirect,
		# so now the last request is not a 'POST' request anymore, and the refresh command works in a more predictable way.
		# (else refresh command will re-issues the last request)
		# This trick is called Post/Redirect/Get pattern
		return redirect(url_for('index'))		
	
	# display list of followed posts
	posts = db.session.scalars(current_user.following_posts()).all()

	# The operation that converts a template into a HTML page is called 'rendering'
	# It is done in Flask using the 'render_template(<filename.html>, <arg>)' function
	# render_templates invokes Jinja template engine (bundled with Flask)
	# Jinja substitutes {{ ... }} block with corresponding values provided in the <arg> of the function 
	return render_template('index.html', title='Home', posts=posts, form=form)

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
		user = db.session.scalar(sqla.select(User).where(User.username == form.username.data))

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

# ========== REGISTER ===========
@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.pwd.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))

	return render_template('register.html', title="Register", form=form)

# ========== USER PROFILE ===========
# Dynamic component in the URL (surrounded by < and >)
@app.route('/user/<username>') 
@login_required
def user(username):
	# db.first_or_404() is a Flask-SQLAlchemy variant of db.session.scalar() that will automatically send a 404 error back to client if no results  
	user = db.first_or_404(sqla.select(User).where(User.username == username))

	# initialize a moke/fake list of posts
	posts = [
		{'author': user, 'body': 'Test post #1'},
		{'author': user, 'body': 'Test post #2'}
	]

	# render the follow or unfollow button
	form = EmptyForm()
	
	return render_template('user.html', user=user, posts=posts, form=form)

# Edit profile
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)

	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()

		flash('Your changes have been saved.')
		return redirect(url_for('edit_profile'))
	
	# pre-populate fields if the form is beeing requested for the first time with a 'GET' request 
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me

	return render_template('edit_profile.html', title='Edit Profile', form=form)	

# Record time of last visit
# Executed right before any view function of the application
@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.now(timezone.utc)

		# No db.session.add() before the commit is needed: this is because when you reference 'current_user', 
		# Flask-Login will already invoke the user loader callback function, which will run a database query 
		# that will put the target user in the database session. 
		db.session.commit()

# Follow route (for a given username)
@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
	form = EmptyForm()

	if form.validate_on_submit():
		user = db.session.scalar(sqla.select(User).where(User.username == username))

		if user is None:
			flash(f'User {username} not found.')
			return redirect(url_for('index'))
		if user == current_user:
			flash('Youn cannot follow yourself!')

		current_user.follow(user)
		db.session.commit()
		flash(f'Now following {username}!')
		return redirect(url_for('user', username=username))
	
	else:
		return redirect(url_for('index'))

# Unfollow route (for a given username)
@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
	form = EmptyForm()    
	
	if form.validate_on_submit():
		user = db.session.scalar(sqla.select(User).where(User.username == username))
        
		if user is None:
			flash(f'User {username} not found.')
			return redirect(url_for('index'))
		if user == current_user:
			flash('You cannot unfollow yourself!')
			return redirect(url_for('user', username=username))

		current_user.unfollow(user)
		db.session.commit()
		flash(f'You are not following {username}.')
		return redirect(url_for('user', username=username))
	else:
		return redirect(url_for('index'))