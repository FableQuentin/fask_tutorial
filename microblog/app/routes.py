# Home page route
# Handles the different URLs that the application supports
# -> in Flask handlers for application routes are written as
#    Python functions called 'view functions'
# -> View functions are mapped to one (or more) URLs
# -> i.e Flask knows what to execute when the client request a given URL  

from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm

# ========== INDEX ===========
# We use decorators to create an association between the URL given as argument and the function
# When a browser requests either of the two URL '/' or '/index', Flask is goinf to invoke this function
# and pass its value back to the browser
@app.route('/')
@app.route('/index')
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


# ========== LOGIN ===========
#  - loading the page, the browser sends the GET request to receive the web page form
#  - Pressing the 'Submit' button in the form will send the POST request
@app.route('/login', methods=['GET', 'POST']) # tells Flask this view accepts GET and POST requests
def login():
	form = LoginForm()
	if form.validate_on_submit():
		# This function will return False when the browser sends the initial GET request for the form
		# The browser will send a POST request as a result of pressing the submit button, this function will gather the data 
		# (run validators attached to the fields) and if everuthing is OK return true
		flash('Login requested from user {}, remember_me={}'.format(
			form.username.data, form.remember_me.data))
		return redirect(url_for('index')) # instruct the client web browser to automatically navigate to the index page
	return render_template('login.html', title='Sign in', form=form)

